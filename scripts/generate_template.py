"""Generate a deployable single-region CloudFormation template from local app sources."""
from pathlib import Path
import base64, io, tarfile, yaml
root=Path(__file__).resolve().parents[1]
archive=io.BytesIO()
with tarfile.open(fileobj=archive, mode='w:gz') as tar:
    for name in ['server.py','index.html']:
        tar.add(root/'app'/name, arcname=name)
encoded=base64.b64encode(archive.getvalue()).decode()
userdata=f'''#!/bin/bash
set -euxo pipefail
mkdir -p /opt/zomato
printf '%s' '{encoded}' | base64 -d | tar -xz -C /opt/zomato
cat > /etc/systemd/system/zomato.service <<'EOF'
[Unit]
Description=Zomato educational demo
After=network.target
[Service]
Environment=PORT=8080
Environment=AWS_REGION=${{AWS::Region}}
ExecStart=/usr/bin/python3 /opt/zomato/server.py
Restart=always
RestartSec=3
User=ec2-user
[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
systemctl enable --now zomato.service
'''
# YAML built with plain strings and CloudFormation-compatible intrinsic objects.
t={
'AWSTemplateFormatVersion':'2010-09-09',
'Description':'Short-lived Zomato demo: ALB, EC2 ASG, CloudWatch scaling, two public AZs. Charges apply.',
'Parameters':{
 'LatestAmiId':{'Type':'AWS::SSM::Parameter::Value<AWS::EC2::Image::Id>','Default':'/aws/service/ami-amazon-linux-latest/al2023-ami-kernel-default-x86_64'},
 'InstanceType':{'Type':'String','Default':'t3.micro','AllowedValues':['t3.micro','t2.micro']},
 'MaxCapacity':{'Type':'Number','Default':2,'MinValue':1,'MaxValue':2},
 'OperatorCidr':{'Type':'String','Default':'0.0.0.0/0','Description':'Restrict to your public IPv4 /32 for private demo; 0.0.0.0/0 allows public HTTP access.'}
},
'Resources':{
 'VPC':{'Type':'AWS::EC2::VPC','Properties':{'CidrBlock':'10.42.0.0/16','EnableDnsSupport':True,'EnableDnsHostnames':True}},
 'IGW':{'Type':'AWS::EC2::InternetGateway'},
 'IGWAttachment':{'Type':'AWS::EC2::VPCGatewayAttachment','Properties':{'VpcId':{'Ref':'VPC'},'InternetGatewayId':{'Ref':'IGW'}}},
 'SubnetA':{'Type':'AWS::EC2::Subnet','Properties':{'VpcId':{'Ref':'VPC'},'CidrBlock':'10.42.1.0/24','AvailabilityZone':{'Fn::Select':[0,{'Fn::GetAZs':''}]},'MapPublicIpOnLaunch':True}},
 'SubnetB':{'Type':'AWS::EC2::Subnet','Properties':{'VpcId':{'Ref':'VPC'},'CidrBlock':'10.42.2.0/24','AvailabilityZone':{'Fn::Select':[1,{'Fn::GetAZs':''}]},'MapPublicIpOnLaunch':True}},
 'RouteTable':{'Type':'AWS::EC2::RouteTable','Properties':{'VpcId':{'Ref':'VPC'}}},
 'DefaultRoute':{'Type':'AWS::EC2::Route','DependsOn':'IGWAttachment','Properties':{'RouteTableId':{'Ref':'RouteTable'},'DestinationCidrBlock':'0.0.0.0/0','GatewayId':{'Ref':'IGW'}}},
 'AssocA':{'Type':'AWS::EC2::SubnetRouteTableAssociation','Properties':{'SubnetId':{'Ref':'SubnetA'},'RouteTableId':{'Ref':'RouteTable'}}},
 'AssocB':{'Type':'AWS::EC2::SubnetRouteTableAssociation','Properties':{'SubnetId':{'Ref':'SubnetB'},'RouteTableId':{'Ref':'RouteTable'}}},
 'AlbSG':{'Type':'AWS::EC2::SecurityGroup','Properties':{'GroupDescription':'Allow demo HTTP to ALB','VpcId':{'Ref':'VPC'},'SecurityGroupIngress':[{'IpProtocol':'tcp','FromPort':80,'ToPort':80,'CidrIp':{'Ref':'OperatorCidr'}}]}},
 'AppSG':{'Type':'AWS::EC2::SecurityGroup','Properties':{'GroupDescription':'Only ALB to demo instances','VpcId':{'Ref':'VPC'},'SecurityGroupIngress':[{'IpProtocol':'tcp','FromPort':8080,'ToPort':8080,'SourceSecurityGroupId':{'Ref':'AlbSG'}}]}},
 'ALB':{'Type':'AWS::ElasticLoadBalancingV2::LoadBalancer','Properties':{'Scheme':'internet-facing','Type':'application','Subnets':[{'Ref':'SubnetA'},{'Ref':'SubnetB'}],'SecurityGroups':[{'Ref':'AlbSG'}]}},
 'TargetGroup':{'Type':'AWS::ElasticLoadBalancingV2::TargetGroup','Properties':{'VpcId':{'Ref':'VPC'},'Port':8080,'Protocol':'HTTP','TargetType':'instance','HealthCheckPath':'/health','HealthCheckIntervalSeconds':15,'HealthyThresholdCount':2}},
 'Listener':{'Type':'AWS::ElasticLoadBalancingV2::Listener','Properties':{'LoadBalancerArn':{'Ref':'ALB'},'Port':80,'Protocol':'HTTP','DefaultActions':[{'Type':'forward','TargetGroupArn':{'Ref':'TargetGroup'}}]}},
 'LaunchTemplate':{'Type':'AWS::EC2::LaunchTemplate','Properties':{'LaunchTemplateData':{'ImageId':{'Ref':'LatestAmiId'},'InstanceType':{'Ref':'InstanceType'},'SecurityGroupIds':[{'Ref':'AppSG'}],'MetadataOptions':{'HttpTokens':'required','HttpEndpoint':'enabled'},'UserData':{'Fn::Base64':{'Fn::Sub':userdata}}}}},
 'ASG':{'Type':'AWS::AutoScaling::AutoScalingGroup','Properties':{'VPCZoneIdentifier':[{'Ref':'SubnetA'},{'Ref':'SubnetB'}],'MinSize':'1','MaxSize':{'Ref':'MaxCapacity'},'DesiredCapacity':'1','HealthCheckType':'ELB','HealthCheckGracePeriod':180,'TargetGroupARNs':[{'Ref':'TargetGroup'}],'LaunchTemplate':{'LaunchTemplateId':{'Ref':'LaunchTemplate'},'Version':{'Fn::GetAtt':['LaunchTemplate','LatestVersionNumber']}}}},
 'ScalingPolicy':{'Type':'AWS::AutoScaling::ScalingPolicy','Properties':{'AutoScalingGroupName':{'Ref':'ASG'},'PolicyType':'TargetTrackingScaling','EstimatedInstanceWarmup':120,'TargetTrackingConfiguration':{'PredefinedMetricSpecification':{'PredefinedMetricType':'ASGAverageCPUUtilization'},'TargetValue':35.0}}}
},
'Outputs':{'LoadBalancerURL':{'Value':{'Fn::Sub':'http://${ALB.DNSName}'}},'AutoScalingGroupName':{'Value':{'Ref':'ASG'}},'TargetGroupArn':{'Value':{'Ref':'TargetGroup'}}}}
path=root/'infra'/'zomato-stack.yaml'
path.write_text(yaml.safe_dump(t,sort_keys=False,width=100000))
print('Generated',path)
