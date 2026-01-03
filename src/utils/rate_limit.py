import time
from collections import defaultdict
from typing import Dict, Tuple

class RateLimiter:
    """Rate limiter to prevent command abuse"""
    
    def __init__(self):
        # Structure: {user_id: {command: [(timestamp, count)]}}
        self.user_commands: Dict[int, Dict[str, list]] = defaultdict(lambda: defaultdict(list))
        # Structure: {user_id: {action: count}}
        self.user_actions: Dict[int, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    
    def check_rate_limit(
        self, 
        user_id: int, 
        command: str, 
        max_uses: int = 5, 
        time_window: int = 60
    ) -> Tuple[bool, float]:
        """
        Check if user has exceeded rate limit for a command
        Returns: (allowed, retry_after)
        """
        current_time = time.time()
        user_commands = self.user_commands[user_id][command]
        
        # Remove old entries outside time window
        user_commands[:] = [
            (ts, count) for ts, count in user_commands 
            if current_time - ts < time_window
        ]
        
        # Count total uses in time window
        total_uses = sum(count for _, count in user_commands)
        
        if total_uses >= max_uses:
            # Calculate retry after
            oldest_time = min(ts for ts, _ in user_commands) if user_commands else current_time
            retry_after = time_window - (current_time - oldest_time)
            return False, retry_after
        
        # Record this use
        user_commands.append((current_time, 1))
        return True, 0.0
    
    def check_action_limit(
        self,
        user_id: int,
        action: str,
        max_actions: int = 10,
        time_window: int = 300
    ) -> Tuple[bool, float]:
        """
        Check if user has exceeded action limit (e.g., ticket creation)
        Returns: (allowed, retry_after)
        """
        current_time = time.time()
        action_key = f"{action}_{user_id}"
        
        # Get action history
        if action_key not in self.user_actions[user_id]:
            self.user_actions[user_id][action_key] = 0
        
        # Simple counter with time-based reset
        # For simplicity, we'll use a sliding window approach
        action_count = self.user_actions[user_id][action_key]
        
        if action_count >= max_actions:
            # Reset after time window (simplified)
            return False, time_window
        
        self.user_actions[user_id][action_key] = action_count + 1
        return True, 0.0
    
    def reset_user(self, user_id: int, command: str = None):
        """Reset rate limit for a user (for moderation)"""
        if command:
            if user_id in self.user_commands and command in self.user_commands[user_id]:
                del self.user_commands[user_id][command]
        else:
            if user_id in self.user_commands:
                del self.user_commands[user_id]
            if user_id in self.user_actions:
                del self.user_actions[user_id]

# Global rate limiter instance
rate_limiter = RateLimiter()

