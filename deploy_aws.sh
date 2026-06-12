#!/bin/bash

# ============================================
# AWS EC2 Deployment Script
# Solar Panel Defect Detection
# ============================================

echo "========================================="
echo "AWS EC2 DEPLOYMENT SCRIPT"
echo "========================================="

# Configuration - CHANGE THESE!
AWS_REGION="us-east-1"
EC2_INSTANCE_TYPE="t2.medium"
KEY_PAIR_NAME="solar-panel-key"
SECURITY_GROUP_NAME="solar-panel-sg"
INSTANCE_NAME="solar-panel-server"

echo ""
echo "Step 1: Create Security Group"
echo "-----------------------------------------"

# Create security group
aws ec2 create-security-group \
    --group-name ${SECURITY_GROUP_NAME} \
    --description "Security group for Solar Panel Detection" \
    --region ${AWS_REGION}

# Add rules
aws ec2 authorize-security-group-ingress \
    --group-name ${SECURITY_GROUP_NAME} \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0 \
    --region ${AWS_REGION}

aws ec2 authorize-security-group-ingress \
    --group-name ${SECURITY_GROUP_NAME} \
    --protocol tcp \
    --port 8000 \
    --cidr 0.0.0.0/0 \
    --region ${AWS_REGION}

aws ec2 authorize-security-group-ingress \
    --group-name ${SECURITY_GROUP_NAME} \
    --protocol tcp \
    --port 5000 \
    --cidr 0.0.0.0/0 \
    --region ${AWS_REGION}

echo "✅ Security group created!"

echo ""
echo "Step 2: Launch EC2 Instance"
echo "-----------------------------------------"

# Launch EC2 instance
INSTANCE_ID=$(aws ec2 run-instances \
    --image-id ami-0c7217cdde317cfec \
    --instance-type ${EC2_INSTANCE_TYPE} \
    --key-name ${KEY_PAIR_NAME} \
    --security-groups ${SECURITY_GROUP_NAME} \
    --tag-specifications "ResourceType=instance,Tags=[{Key=Name,Value=${INSTANCE_NAME}}]" \
    --region ${AWS_REGION} \
    --query 'Instances[0].InstanceId' \
    --output text)

echo "Instance ID: ${INSTANCE_ID}"

echo ""
echo "Step 3: Wait for Instance to Start"
echo "-----------------------------------------"

aws ec2 wait instance-running \
    --instance-ids ${INSTANCE_ID} \
    --region ${AWS_REGION}

# Get public IP
PUBLIC_IP=$(aws ec2 describe-instances \
    --instance-ids ${INSTANCE_ID} \
    --region ${AWS_REGION} \
    --query 'Reservations[0].Instances[0].PublicIpAddress' \
    --output text)

echo "Public IP: ${PUBLIC_IP}"

echo ""
echo "Step 4: Install Docker on EC2"
echo "-----------------------------------------"

# SSH and install Docker
ssh -o StrictHostKeyChecking=no -i ${KEY_PAIR_NAME}.pem ubuntu@${PUBLIC_IP} << 'EOF'
    sudo apt-get update
    sudo apt-get install -y docker.io docker-compose git
    sudo systemctl start docker
    sudo systemctl enable docker
    sudo usermod -aG docker ubuntu
    echo "✅ Docker installed!"
EOF

echo ""
echo "Step 5: Clone and Deploy Application"
echo "-----------------------------------------"

ssh -i ${KEY_PAIR_NAME}.pem ubuntu@${PUBLIC_IP} << 'EOF'
    # Clone repository
    git clone https://github.com/iram-mulla/solar-panel-devops.git
    cd solar-panel-devops
    
    # Build and start containers
    sudo docker-compose up -d
    
    echo "✅ Application deployed!"
EOF

echo ""
echo "========================================="
echo "DEPLOYMENT COMPLETE!"
echo "========================================="
echo ""
echo "Your Application URLs:"
echo "  Web App:  http://${PUBLIC_IP}:8000"
echo "  MLflow:   http://${PUBLIC_IP}:5000"
echo ""
echo "To SSH into instance:"
echo "  ssh -i ${KEY_PAIR_NAME}.pem ubuntu@${PUBLIC_IP}"