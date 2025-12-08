# backend/utils/monitoring.py
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from collections import defaultdict
import threading

class ClaimsMonitor:
    """
    Real-time monitoring and metrics tracking for claims processing
    """
    def __init__(self):
        self.metrics = {
            "total_claims": 0,
            "approved": 0,
            "rejected": 0,
            "manual_review": 0,
            "errors": 0,
            "total_processing_time": 0.0,
            "fraud_high": 0,
            "fraud_medium": 0,
            "fraud_low": 0,
            "agent_times": {
                "extraction": [],
                "rag": [],
                "validation": [],
                "fraud": [],
                "decision": [],
                "summary": []
            }
        }
        self.claims_log = []
        self.lock = threading.Lock()
        self.log_file = Path("logs/claims_processing.log")
        self.log_file.parent.mkdir(exist_ok=True)
    
    def start_claim(self, claim_id: str) -> Dict[str, Any]:
        """Start tracking a new claim"""
        return {
            "claim_id": claim_id,
            "start_time": time.time(),
            "agent_times": {}
        }
    
    def track_agent(self, tracking: Dict, agent_name: str):
        """Context manager to track agent execution time"""
        class AgentTimer:
            def __init__(self, monitor, tracking, agent):
                self.monitor = monitor
                self.tracking = tracking
                self.agent = agent
                self.start = None
            
            def __enter__(self):
                self.start = time.time()
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                elapsed = time.time() - self.start
                self.tracking["agent_times"][self.agent] = elapsed
                with self.monitor.lock:
                    self.monitor.metrics["agent_times"][self.agent].append(elapsed)
        
        return AgentTimer(self, tracking, agent_name)
    
    def complete_claim(self, tracking: Dict, result: Dict[str, Any], error: str = None):
        """Complete claim tracking and update metrics"""
        with self.lock:
            total_time = time.time() - tracking["start_time"]
            
            # Update counters
            self.metrics["total_claims"] += 1
            self.metrics["total_processing_time"] += total_time
            
            if error:
                self.metrics["errors"] += 1
            else:
                # Track decision
                decision = result.get("final_decision", {}).get("decision", "UNKNOWN")
                if decision == "APPROVE":
                    self.metrics["approved"] += 1
                elif decision == "REJECT":
                    self.metrics["rejected"] += 1
                elif decision == "MANUAL_REVIEW":
                    self.metrics["manual_review"] += 1
                
                # Track fraud level
                fraud_level = result.get("fraud", {}).get("risk_level", "LOW")
                if fraud_level == "HIGH":
                    self.metrics["fraud_high"] += 1
                elif fraud_level == "MEDIUM":
                    self.metrics["fraud_medium"] += 1
                else:
                    self.metrics["fraud_low"] += 1
            
            # Log the claim
            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "claim_id": tracking["claim_id"],
                "total_time": round(total_time, 2),
                "agent_times": {k: round(v, 2) for k, v in tracking["agent_times"].items()},
                "decision": result.get("final_decision", {}).get("decision") if not error else "ERROR",
                "fraud_level": result.get("fraud", {}).get("risk_level") if not error else None,
                "error": error
            }
            
            self.claims_log.append(log_entry)
            
            # Write to log file
            with open(self.log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics snapshot"""
        with self.lock:
            total = self.metrics["total_claims"]
            if total == 0:
                return {
                    "message": "No claims processed yet",
                    "metrics": self.metrics
                }
            
            avg_time = self.metrics["total_processing_time"] / total
            
            # Calculate agent averages
            agent_avg = {}
            for agent, times in self.metrics["agent_times"].items():
                if times:
                    agent_avg[agent] = {
                        "avg_time": round(sum(times) / len(times), 2),
                        "min_time": round(min(times), 2),
                        "max_time": round(max(times), 2),
                        "total_calls": len(times)
                    }
            
            return {
                "summary": {
                    "total_claims": total,
                    "approved": self.metrics["approved"],
                    "rejected": self.metrics["rejected"],
                    "manual_review": self.metrics["manual_review"],
                    "errors": self.metrics["errors"],
                    "approval_rate": round((self.metrics["approved"] / total) * 100, 1),
                    "rejection_rate": round((self.metrics["rejected"] / total) * 100, 1),
                    "avg_processing_time": round(avg_time, 2)
                },
                "fraud_detection": {
                    "high_risk": self.metrics["fraud_high"],
                    "medium_risk": self.metrics["fraud_medium"],
                    "low_risk": self.metrics["fraud_low"]
                },
                "agent_performance": agent_avg,
                "recent_claims": self.claims_log[-10:]  # Last 10 claims
            }
    
    def get_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        with self.lock:
            lines = [
                "# HELP claims_total Total number of claims processed",
                f"claims_total {self.metrics['total_claims']}",
                "",
                "# HELP claims_approved Number of approved claims",
                f"claims_approved {self.metrics['approved']}",
                "",
                "# HELP claims_rejected Number of rejected claims",
                f"claims_rejected {self.metrics['rejected']}",
                "",
                "# HELP claims_manual_review Number of claims needing manual review",
                f"claims_manual_review {self.metrics['manual_review']}",
                "",
                "# HELP claims_errors Number of processing errors",
                f"claims_errors {self.metrics['errors']}",
                "",
                "# HELP fraud_high_risk Number of high risk fraud detections",
                f"fraud_high_risk {self.metrics['fraud_high']}",
                "",
                "# HELP fraud_medium_risk Number of medium risk fraud detections",
                f"fraud_medium_risk {self.metrics['fraud_medium']}",
                "",
                "# HELP fraud_low_risk Number of low risk fraud detections",
                f"fraud_low_risk {self.metrics['fraud_low']}",
                ""
            ]
            
            # Add agent timing metrics
            for agent, times in self.metrics["agent_times"].items():
                if times:
                    avg = sum(times) / len(times)
                    lines.append(f"# HELP agent_{agent}_avg_seconds Average processing time for {agent} agent")
                    lines.append(f"agent_{agent}_avg_seconds {avg:.3f}")
                    lines.append("")
            
            return "\n".join(lines)

# Global monitor instance
monitor = ClaimsMonitor()