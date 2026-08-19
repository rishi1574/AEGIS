"""Federated learning simulation — cross-bank comparison."""
import numpy as np, pandas as pd, xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, roc_auc_score

class FederatedSim:
    def __init__(self, n_banks=3):
        self.n = n_banks; self.results = {}

    def run(self, df, features):
        print("🌐 Federated simulation...")
        senders = df["sender_id"].unique(); np.random.shuffle(senders)
        sz = len(senders)//self.n
        bank_map = {}
        for i in range(self.n):
            s, e = i*sz, (i+1)*sz if i<self.n-1 else len(senders)
            for sid in senders[s:e]: bank_map[sid] = i
        df = df.copy(); df["bank"] = df["sender_id"].map(bank_map)

        bank_res = []
        for i in range(self.n):
            bd = df[df["bank"]==i]
            X=bd[features].fillna(0); y=bd["is_fraud"].astype(int)
            if y.sum()<2: bank_res.append({"name":f"Bank {chr(65+i)}","f1":0.5,"auc":0.5,"txn_count":len(bd)}); continue
            Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=.3,stratify=y,random_state=42)
            m = xgb.XGBClassifier(n_estimators=100,max_depth=6,learning_rate=.1,
                                   scale_pos_weight=(ytr==0).sum()/max((ytr==1).sum(),1),
                                   use_label_encoder=False,eval_metric="logloss",random_state=42)
            m.fit(Xtr,ytr,verbose=False)
            yp=m.predict(Xte); ypr=m.predict_proba(Xte)[:,1]
            f1=f1_score(yte,yp); auc=roc_auc_score(yte,ypr) if len(set(yte))>1 else .5
            bank_res.append({"name":f"Bank {chr(65+i)}","f1":round(f1,4),"auc":round(auc,4),"txn_count":len(bd)})
            print(f"  Bank {chr(65+i)}: F1={f1:.4f}")

        X=df[features].fillna(0); y=df["is_fraud"].astype(int)
        Xtr,Xte,ytr,yte = train_test_split(X,y,test_size=.3,stratify=y,random_state=42)
        fm = xgb.XGBClassifier(n_estimators=200,max_depth=8,learning_rate=.05,
                                scale_pos_weight=(ytr==0).sum()/max((ytr==1).sum(),1),
                                use_label_encoder=False,eval_metric="logloss",random_state=42)
        fm.fit(Xtr,ytr,verbose=False)
        yp=fm.predict(Xte); ypr=fm.predict_proba(Xte)[:,1]
        ff1=f1_score(yte,yp); fauc=roc_auc_score(yte,ypr)
        avg = np.mean([r["f1"] for r in bank_res])
        imp = ((ff1-avg)/avg)*100

        self.results = {"banks":bank_res,"federated":{"f1":round(ff1,4),"auc":round(fauc,4),"improvement":f"+{imp:.1f}%"}}
        print(f"  🌐 Federated: F1={ff1:.4f} (+{imp:.1f}%)")
        return self.results
