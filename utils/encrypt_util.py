import hashlib
import bcrypt
from typing import Union, Tuple

class BcryptSecurity:
    @staticmethod
    def hash_password(
        plain_password: str,
        rounds: int = 12
    ) -> Tuple[bytes, bytes]:
        """
        密码哈希函数（自动加盐）
        :param plain_password: 明文密码字符串
        :param rounds: 工作因子（建议12-14）
        :return: (盐值, 哈希值)
        """
        # 生成随机盐（自动包含工作因子参数）
        salt = bcrypt.gensalt(rounds=rounds)  # 默认生成22字节盐[1,6](@ref)
        # 哈希处理（自动拼接密码和盐）
        hashed = bcrypt.hashpw(plain_password.encode('utf-8'), salt)
        return salt, hashed

    @staticmethod
    def verify_password(
        plain_password: str,
        stored_hash: Union[bytes, str]
    ) -> bool:
        """
        密码验证函数（防时序攻击）
        :param plain_password: 待验证密码
        :param stored_hash: 数据库存储的哈希值
        """
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode('utf-8')
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            stored_hash
        )
def md5_string(text: str, encoding: str = 'utf-8') -> str:
    """安全计算字符串的 MD5（可指定编码）"""
    return hashlib.md5(text.encode(encoding)).hexdigest()

if __name__ == "__main__":
    # input_text = input("请输入要计算 MD5 的字符串: ")
    # print("MD5 哈希值:", md5_string(input_text))
    # 注册流程
    user_password = "MySecureP@ssw0rd"
    salt, hashed = BcryptSecurity.hash_password(user_password)

    # 存储到数据库（建议同时保存盐和哈希）
    print(f"Salt: {salt.decode()}")
    print(f"Hash: {hashed.decode()}")

    # 登录验证流程
    input_password = "MySecureP@ssw0rd"
    is_valid = BcryptSecurity.verify_password(input_password, hashed)
    print(f"验证结果: {is_valid}")  # 输出 True