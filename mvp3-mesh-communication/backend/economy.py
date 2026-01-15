"""
Economic system for MVP B2
Implements micro-incentive economy with Wallet and Reputation management
"""

from typing import Dict, Optional
from datetime import datetime
import numpy as np


# Economic Constants
INITIAL_CREDITS = 100  # Starting balance for new nodes
UBI_AMOUNT = 5  # Universal Basic Income per drip interval
UBI_INTERVAL_TICKS = 10  # How often UBI is distributed

# Message Type Costs and Rewards
LOGISTICS_SEND_COST = 2  # Cost to send a Logistics packet (deflationary)
LOGISTICS_RELAY_REWARD = 1  # Reward for relaying Logistics (must be < send_cost)
SAFETY_SEND_COST = 0  # Safety packets are always free to send
SAFETY_RELAY_REWARD = 10  # High reward for relaying Safety (inflationary, public good)


class Wallet:
    """
    Manages a node's credit balance.
    Credits are the currency of the network economy.
    """
    
    def __init__(self, node_id: int, initial_credits: int = INITIAL_CREDITS):
        self.node_id = node_id
        self.balance = initial_credits
        self.total_earned = 0
        self.total_spent = 0
        self.transaction_count = 0
        
    def add_credits(self, amount: float, reason: str = ""):
        """
        Add credits to wallet (earned from relaying or UBI).
        
        Args:
            amount: Credits to add
            reason: Optional description of why credits were added
        """
        if amount > 0:
            self.balance += amount
            self.total_earned += amount
            self.transaction_count += 1
            
    def spend_credits(self, amount: float, reason: str = "") -> bool:
        """
        Attempt to spend credits (for sending messages).
        
        Args:
            amount: Credits to spend
            reason: Optional description of expense
            
        Returns:
            True if transaction succeeded, False if insufficient funds
        """
        if amount <= 0:
            return True  # Free transactions always succeed
            
        if self.balance >= amount:
            self.balance -= amount
            self.total_spent += amount
            self.transaction_count += 1
            return True
        else:
            # Insufficient funds
            return False
    
    def get_balance(self) -> float:
        """Get current credit balance"""
        return self.balance
    
    def get_stats(self) -> dict:
        """Get wallet statistics"""
        return {
            "node_id": self.node_id,
            "balance": round(self.balance, 2),
            "total_earned": round(self.total_earned, 2),
            "total_spent": round(self.total_spent, 2),
            "transaction_count": self.transaction_count,
            "net_profit": round(self.total_earned - self.total_spent, 2)
        }


class ReputationManager:
    """
    Manages reputation scores for peer nodes.
    Distinguishes between malicious (packet dropping) and slow (weak connection) nodes.
    
    Each node maintains its own local reputation scores for its neighbors.
    """
    
    def __init__(self, node_id: int):
        self.node_id = node_id
        # Dict[peer_node_id -> {"sent": int, "relayed": int}]
        self.peer_stats: Dict[int, Dict[str, int]] = {}
        
    def record_packet_sent_to_peer(self, peer_id: int):
        """
        Record that we forwarded a packet to a peer.
        
        Args:
            peer_id: The node we sent the packet to
        """
        if peer_id not in self.peer_stats:
            self.peer_stats[peer_id] = {"sent": 0, "relayed": 0}
        self.peer_stats[peer_id]["sent"] += 1
        
    def record_successful_relay_by_peer(self, peer_id: int):
        """
        Record that a peer successfully relayed a packet onward.
        
        Args:
            peer_id: The node that relayed the packet
        """
        if peer_id not in self.peer_stats:
            self.peer_stats[peer_id] = {"sent": 0, "relayed": 0}
        self.peer_stats[peer_id]["relayed"] += 1
        
    def get_reputation_score(self, peer_id: int) -> float:
        """
        Calculate reputation score for a peer.
        Score = packets_successfully_relayed / packets_received_for_relay
        
        Returns:
            Float between 0.0 (malicious/unreliable) and 1.0 (perfect reliability)
            Returns 1.0 if no data yet (optimistic default)
        """
        if peer_id not in self.peer_stats:
            return 1.0  # Optimistic: trust new nodes initially
            
        stats = self.peer_stats[peer_id]
        if stats["sent"] == 0:
            return 1.0
            
        # Key formula: reputation = relayed / sent
        reputation = stats["relayed"] / stats["sent"]
        return min(1.0, reputation)  # Cap at 1.0
        
    def is_peer_trusted(self, peer_id: int, threshold: float = 0.7) -> bool:
        """
        Check if a peer is trusted (above reputation threshold).
        
        Args:
            peer_id: Peer to check
            threshold: Minimum reputation score (default 0.7 = 70%)
            
        Returns:
            True if peer is trusted
        """
        return self.get_reputation_score(peer_id) >= threshold
        
    def get_all_reputations(self) -> Dict[int, float]:
        """Get reputation scores for all known peers"""
        return {
            peer_id: self.get_reputation_score(peer_id)
            for peer_id in self.peer_stats.keys()
        }
    
    def get_stats(self) -> dict:
        """Get detailed reputation statistics"""
        return {
            "node_id": self.node_id,
            "peer_count": len(self.peer_stats),
            "reputations": self.get_all_reputations(),
            "detailed_stats": self.peer_stats
        }


class EconomyTracker:
    """
    Global tracker for network-wide economic metrics.
    Calculates KPIs like Gini coefficient and Nakamoto coefficient.
    """
    
    def __init__(self):
        self.total_transactions = 0
        self.total_fee_revenue = 0.0  # Sum of all Logistics send_costs
        self.total_safety_subsidies = 0.0  # Sum of all Safety relay_rewards (minted)
        self.tick_count = 0
        
    def record_transaction(self, transaction_type: str, amount: float):
        """
        Record a transaction for statistics.
        
        Args:
            transaction_type: 'logistics_send', 'logistics_relay', 'safety_relay', 'ubi'
            amount: Credit amount
        """
        self.total_transactions += 1
        
        if transaction_type == 'logistics_send':
            self.total_fee_revenue += amount
        elif transaction_type == 'safety_relay':
            self.total_safety_subsidies += amount
            
    def increment_tick(self):
        """Increment the global simulation tick counter"""
        self.tick_count += 1
        
    def calculate_gini_coefficient(self, wallets: list) -> float:
        """
        Calculate Gini coefficient for wealth inequality.
        
        0.0 = Perfect equality (everyone has same credits)
        1.0 = Perfect inequality (one node has everything)
        
        High Gini (>0.8) indicates failure: credits concentrated in few nodes.
        
        Args:
            wallets: List of Wallet objects
            
        Returns:
            Gini coefficient (0.0 to 1.0)
        """
        if not wallets:
            return 0.0
            
        balances = [w.balance for w in wallets]
        balances = np.array(sorted(balances))
        n = len(balances)
        
        if n == 0 or balances.sum() == 0:
            return 0.0
            
        # Gini calculation using numpy
        index = np.arange(1, n + 1)
        gini = (2 * np.sum(index * balances)) / (n * np.sum(balances)) - (n + 1) / n
        
        return round(gini, 4)
        
    def calculate_nakamoto_coefficient(self, wallets: list) -> int:
        """
        Calculate Nakamoto coefficient: minimum number of nodes to control >50% of credits.
        
        Low Nakamoto (2-3) indicates centralization risk.
        
        Args:
            wallets: List of Wallet objects
            
        Returns:
            Number of top nodes needed to control >50% of total credits
        """
        if not wallets:
            return 0
            
        balances = sorted([w.balance for w in wallets], reverse=True)
        total = sum(balances)
        
        if total == 0:
            return len(wallets)
            
        cumulative = 0
        for i, balance in enumerate(balances):
            cumulative += balance
            if cumulative > total * 0.5:
                return i + 1
                
        return len(wallets)
        
    def get_economy_stats(self, wallets: list) -> dict:
        """
        Get comprehensive economy statistics.
        
        Args:
            wallets: List of all node Wallet objects
            
        Returns:
            Dictionary with all KPIs
        """
        gini = self.calculate_gini_coefficient(wallets)
        nakamoto = self.calculate_nakamoto_coefficient(wallets)
        
        total_credits = sum(w.balance for w in wallets)
        avg_balance = total_credits / len(wallets) if wallets else 0
        
        return {
            "tick_count": self.tick_count,
            "total_transactions": self.total_transactions,
            "total_fee_revenue": round(self.total_fee_revenue, 2),
            "total_safety_subsidies": round(self.total_safety_subsidies, 2),
            "total_credits_in_circulation": round(total_credits, 2),
            "average_balance": round(avg_balance, 2),
            "gini_coefficient": gini,
            "nakamoto_coefficient": nakamoto,
            "health_status": self._assess_health(gini, nakamoto)
        }
        
    def _assess_health(self, gini: float, nakamoto: int) -> str:
        """
        Assess overall economic health.
        
        Args:
            gini: Gini coefficient
            nakamoto: Nakamoto coefficient
            
        Returns:
            Health status string
        """
        if gini > 0.8 or nakamoto < 3:
            return "CRITICAL - High centralization risk"
        elif gini > 0.6 or nakamoto < 5:
            return "WARNING - Moderate inequality"
        else:
            return "HEALTHY - Well distributed"


# Global economy tracker instance
global_economy = EconomyTracker()
