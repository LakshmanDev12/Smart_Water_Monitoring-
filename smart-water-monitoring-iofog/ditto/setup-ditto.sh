#!/bin/bash
# ============================================
# Eclipse Ditto Setup Script (Bash)
# Creates digital twin policy and things for
# Smart Water Quality Monitoring
# ============================================

DITTO_URL="http://localhost:8085"
MAX_RETRIES=30
RETRY_DELAY=5

echo "============================================"
echo "  Eclipse Ditto - Digital Twin Setup"
echo "============================================"
echo ""

# Step 1: Wait for Ditto to be healthy
echo "[1/3] Waiting for Ditto to be ready..."
retries=0
ditto_ready=false

while [ "$ditto_ready" = false ] && [ $retries -lt $MAX_RETRIES ]; do
    if curl -sf "$DITTO_URL/health" > /dev/null 2>&1; then
        ditto_ready=true
        echo "  ✅ Ditto is healthy!"
    else
        retries=$((retries + 1))
        echo "  Attempt $retries/$MAX_RETRIES - Ditto not ready. Retrying in ${RETRY_DELAY}s..."
        sleep $RETRY_DELAY
    fi
done

if [ "$ditto_ready" = false ]; then
    echo "  ❌ ERROR: Ditto did not become healthy after $MAX_RETRIES attempts."
    echo "  Make sure Docker containers are running: docker compose ps"
    exit 1
fi

# Step 2: Create Policy
echo ""
echo "[2/3] Creating tank policy..."

curl -sf -X PUT "$DITTO_URL/api/2/policies/water:tank-policy" \
  -H 'Content-Type: application/json' \
  -d '{
    "entries": {
      "DEFAULT": {
        "subjects": {
          "nginx:ditto": {
            "type": "pre-authenticated connection"
          }
        },
        "resources": {
          "thing:/": {
            "grant": ["READ", "WRITE"],
            "revoke": []
          },
          "policy:/": {
            "grant": ["READ", "WRITE"],
            "revoke": []
          },
          "message:/": {
            "grant": ["READ", "WRITE"],
            "revoke": []
          }
        }
      }
    }
  }' && echo "  ✅ Policy created!" || echo "  ⚠️ Policy may already exist (OK)"

# Step 3: Create Things
echo ""
echo "[3/3] Creating digital twins..."

for TANK_ID in TANK001 TANK002 TANK003; do
    curl -sf -X PUT "$DITTO_URL/api/2/things/water:$TANK_ID" \
      -H 'Content-Type: application/json' \
      -d "{
        \"policyId\": \"water:tank-policy\",
        \"attributes\": {
          \"tankId\": \"$TANK_ID\",
          \"description\": \"Smart Water Tank $TANK_ID\",
          \"location\": \"Plant Floor\"
        },
        \"features\": {
          \"waterQuality\": {
            \"properties\": {
              \"pH\": 7.0,
              \"turbidity\": 0.0,
              \"temperature\": 25.0,
              \"waterLevel\": 50.0,
              \"status\": \"UNKNOWN\",
              \"alerts\": [],
              \"timestamp\": \"\"
            }
          }
        }
      }" && echo "  ✅ Digital twin water:$TANK_ID created!" || echo "  ⚠️ water:$TANK_ID may already exist (OK)"
done

echo ""
echo "============================================"
echo "  Setup Complete!"
echo "============================================"
echo ""
echo "  Verify twins:"
echo "    curl http://localhost:8085/api/2/things/water:TANK001"
echo "    curl http://localhost:8085/api/2/things/water:TANK002"
echo "    curl http://localhost:8085/api/2/things/water:TANK003"
echo ""
