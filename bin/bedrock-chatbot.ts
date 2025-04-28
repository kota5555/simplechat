#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from 'aws-cdk-lib';
import { BedrockChatbotStack } from '../lib/bedrock-chatbot-stack';

// 型定義をここで正しく指定するために追加
import { StackProps } from 'aws-cdk-lib';

interface BedrockChatbotStackProps extends StackProps {
  modelId: string;
}

const app = new cdk.App();

// スタック作成
new BedrockChatbotStack(app, 'BedrockChatbotStack', {
  modelId: 'us.amazon.nova-lite-v1:0',
  env: { 
    account: process.env.CDK_DEFAULT_ACCOUNT, 
    region: process.env.CDK_DEFAULT_REGION || 'us-east-1',
  },
} as BedrockChatbotStackProps);

// タグ追加
cdk.Tags.of(app).add('Project', 'BedrockChatbot');
cdk.Tags.of(app).add('Environment', 'Dev');

