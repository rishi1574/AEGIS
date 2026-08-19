class EnsembleModel:
    """
    Combines XGBoost, GNN, and Transformer scores.
    """
    def __init__(self, xgb_model=None, gnn_model=None, transformer_model=None):
        self.xgb = xgb_model
        self.gnn = gnn_model
        self.transformer = transformer_model
        
    def predict(self, txn_features, graph_node_id, sequence):
        xgb_score = self.xgb.predict(txn_features)['risk_score'] if self.xgb else 0.1
        gnn_score = self.gnn.predict(graph_node_id) if self.gnn else 0.1
        trans_score = self.transformer.predict(sequence) if self.transformer else 0.1
        
        # Simple average ensemble
        final_score = (xgb_score * 0.6) + (gnn_score * 0.2) + (trans_score * 0.2)
        return {"risk_score": final_score, "is_fraud": final_score > 0.5}
