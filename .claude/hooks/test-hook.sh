#!/bin/bash
# Simple test hook - just echo to confirm it fires
echo "🔔 HOOK FIRED at $(date +%H:%M:%S)"
echo "   Received stdin:"
cat | head -5
