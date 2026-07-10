"""
认证服务
"""

from fastapi import HTTPException, Header
from typing import Optional
import logging

from .config import VALID_TOKENS

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthService:
    """认证服务类"""
    
    def __init__(self):
        self.valid_tokens = VALID_TOKENS
    
    def verify_auth_token(self, authorization: Optional[str] = Header(None)) -> str:
        """
        验证Authorization Header中的Bearer Token
        
        Args:
            authorization: Authorization header值
            
        Returns:
            验证通过的token
            
        Raises:
            HTTPException: 认证失败时抛出
        """
        logger.info(f"验证认证token: {authorization}")
        
        if not authorization:
            logger.warning("缺少Authorization Header")
            raise HTTPException(status_code=401, detail="Missing Authorization Header")
        
        try:
            scheme, _, token = authorization.partition(" ")
            
            if scheme.lower() != "bearer":
                logger.warning(f"无效的认证方案: {scheme}")
                raise HTTPException(status_code=401, detail="Invalid Authorization scheme")
            
            if not token:
                logger.warning("Token为空")
                raise HTTPException(status_code=403, detail="Token is empty")
            
            if token not in self.valid_tokens:
                logger.warning(f"无效或过期的Token: {token}")
                raise HTTPException(status_code=403, detail="Invalid or Expired Token")
            
            logger.info(f"Token验证成功: {token}")
            return token
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Token验证过程中发生错误: {str(e)}")
            raise HTTPException(status_code=500, detail="Internal authentication error")
    
    def add_token(self, token: str) -> bool:
        """
        添加新的有效token
        
        Args:
            token: 新的token
            
        Returns:
            是否添加成功
        """
        if token not in self.valid_tokens:
            self.valid_tokens.append(token)
            logger.info(f"添加新token: {token}")
            return True
        return False
    
    def remove_token(self, token: str) -> bool:
        """
        移除token
        
        Args:
            token: 要移除的token
            
        Returns:
            是否移除成功
        """
        if token in self.valid_tokens:
            self.valid_tokens.remove(token)
            logger.info(f"Token移除成功: {token}")
            return True
        return False
    
    def get_valid_tokens(self) -> list:
        """
        获取所有有效token列表
        
        Returns:
            有效token列表
        """
        return self.valid_tokens.copy()
    
    def is_token_valid(self, token: str) -> bool:
        """
        检查token是否有效
        
        Args:
            token: 要检查的token
            
        Returns:
            token是否有效
        """
        return token in self.valid_tokens
