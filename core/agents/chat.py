from pocketflow import BatchNode, Node, Flow

class ChunkDocs(BatchNode):
    def prep(self, shared):
        return shared["files"]  # 文件路径列表
    def exec(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        size = 500
        return [text[i : i + size] for i in range(0, len(text), size)]
    def post(self, shared, prep_res, exec_res_list):
        shared["all_chunks"] = sum(exec_res_list, [])

class EmbedDocs(BatchNode):
    def prep(self, shared):
        return shared["all_chunks"]
    def exec(self, chunk):
        return get_embedding(chunk)
    def post(self, shared, prep_res, exec_res_list):
        shared["all_embeds"] = exec_res_list
        print(f"共生成嵌入向量：{len(exec_res_list)}")  # 用于调试

class StoreIndex(Node):
    def prep(self, shared):
        return shared["all_embeds"]
    def exec(self, embeds):
        return create_index(embeds)
    def post(self, shared, prep_res, index):
        shared["index"] = index
        print("索引存储完成")
