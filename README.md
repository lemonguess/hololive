## 大纲
### 1.智能体配置
仅支持 openai 格式

1. llm 模型选择；
2. MCP 配置；
3. 角色 prompt；

#### 1.2 模型类别区分
1. LLMModels
2. EmbeddingModels
3. RerankModels
4. ASRModels
5. TTSModels

#### 1.3 技术选型：langchain
1.基础供应商管理表
- id => int,
- provider_uuid => varchar(255),
- icon => text,
- name => varchar(255),
- description => text,
- update_time => datetime,
- create_time => datetime,
- 
2.用户的供应商管理
- id => int,
- user_uuid => varchar(255),
- provider_uuid => varchar(255),
- user_provider_uuid => varchar(255),
- api_key => text,
- update_time => datetime,
- create_time => datetime,
- 
3.LLM 管理
- id => int,
- llm_uuid => varchar(255),
- user_provider_uuid => varchar(255),
- user_uuid => varchar(255),
- name => varchar(255),
- max_tokens => int,
- context_length => int,
- update_time => datetime,
- create_time => datetime,
- 
4.智能体配置管理
- id => int,
- agent_uuid => varchar(255),
- llm_uuid => varchar(255),
- user_uuid => varchar(255),
- agent_name => varchar(255),
- description => text,
- icon => text,
- system_prompt => text,
- opening_statement => text,
- knowledge_config => json,
- memory_config => json,
- websearch_config => json,
- mcp_config => json,
- update_time => datetime,
- create_time => datetime,

==> 我的智能体uuid
### 2.tts 语音 配置
1. 音色；
2. 语言；
3. 情绪(动态？角色绑定？)
4. 音色克隆

tts配置信息表字段：
- id => int,
- name => varchar(255),
- description => text,
- voice_uuid => varchar(255),
- tts_type => int,
- charactor => varchar(255),
- default_emotion => varchar(255),
- default_language => varchar(255),
- configs => json,
- created_at => datetime,
- updated_at => datetime,

==> 我的音色uuid

### 3.形象配置
1. 动作编排
2. 接入多模态大模型，实现视频通话
3. 实现语音通话