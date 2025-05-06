from models.fields import AgentMemory, AgentModel, AgentKnowledge, AgentWebSearch, AgentFileParser, AgentMCP


class Agent:
    """
    智能体覆盖内容：
    0.编排模块能力；
    1.长期记忆模块；
    2.知识库配置模块；
    3.网络搜索模块；
    4.文件解析能力；
    5.MCP调用能力；
    """
    def __init__(self,
                 memory: AgentMemory,
                 model: AgentModel,
                 knowledge: AgentKnowledge,
                 websearch: AgentWebSearch,
                 file_parser: AgentFileParser,
                 mcp: AgentMCP,
                 ):
        pass

def get_agent_client(agent_id) -> Agent:
    # TODO 通过 agent_id，配置出完整的 agent 对象
    return Agent()


if __name__ == "__main__":
    run_chat_memory_demo()