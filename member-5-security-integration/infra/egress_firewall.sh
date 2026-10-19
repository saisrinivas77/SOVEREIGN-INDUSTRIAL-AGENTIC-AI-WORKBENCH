#!/usr/bin/env bash
# Sovereign AI Workbench — Host & Container Egress Firewall Script
# Enforces Default-Deny Outbound Network Policy for confidential execution.

set -euo pipefail

echo "============================================================"
echo "Applying Sovereign Egress Firewall Policy: DEFAULT DENY"
echo "============================================================"

# Flush existing custom egress chains
iptables -F OUTPUT || true

# Allow loopback (127.0.0.1 / localhost)
iptables -A OUTPUT -o lo -j ACCEPT

# Allow established/related incoming connections
iptables -A OUTPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow local network to approved services (e.g. Ollama on 11434, local Chroma on 8001)
iptables -A OUTPUT -d 127.0.0.1 -p tcp -m multiport --dports 8000,8001,11434,3000,5000 -j ACCEPT

# Drop and log any other outbound traffic
iptables -A OUTPUT -j LOG --log-prefix "[SOVEREIGN_EGRESS_BLOCKED] " --log-level 4
iptables -A OUTPUT -j REJECT --reject-with icmp-admin-prohibited

echo "Sovereign Egress Firewall rules successfully applied."
