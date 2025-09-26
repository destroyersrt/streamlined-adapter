#!/bin/bash

# DEPRECATED: Use deploy-agent.sh instead
# 
# This script is kept for backward compatibility but the new
# deploy-agent.sh script is much simpler and better.
#
# New usage: bash deploy-agent.sh helpful my_agent sk-ant-xxxxx

echo "⚠️  DEPRECATED SCRIPT"
echo "===================="
echo ""
echo "This aws-deploy.sh script is deprecated."
echo "Please use one of the new deployment scripts instead:"
echo ""
echo "🆕 For complete AWS EC2 deployment:"
echo "  bash scripts/aws-ec2-deploy.sh helpful my_agent sk-ant-xxxxx"
echo ""
echo "📡 For existing server deployment:"
echo "  bash scripts/deploy-agent.sh helpful my_agent sk-ant-xxxxx"
echo ""
echo "The new script is:"
echo "• ✅ Much simpler (no SSL complexity)"  
echo "• ✅ Uses new streamlined adapter"
echo "• ✅ Supports multiple agent types"
echo "• ✅ Works on Ubuntu and Amazon Linux"
echo ""
echo "Available agent types: helpful, pirate, echo, analyst"
echo ""
exit 1