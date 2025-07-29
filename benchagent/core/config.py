import os
from dataclasses import dataclass
from typing import Dict, Any, Optional
import json


@dataclass
class LLMConfig:
    """LLM configuration"""
    model: str
    api_key: str
    base_url: Optional[str] = None
    temperature: float = 0.1
    max_tokens: int = 4000
    timeout: int = 60


@dataclass
class BlockchainConfig:
    """Blockchain configuration"""
    rpc_url: str
    private_key: str
    sender_address: str
    chain_id: int = 1
    gas_limit: int = 8000000
    gas_price_multiplier: float = 1.1


@dataclass
class BenchmarkConfig:
    """Benchmark test configuration"""
    llm: LLMConfig
    blockchain: BlockchainConfig
    max_retries: int = 3
    timeout: int = 300
    output_dir: str = "outputs"
    solc_version: str = "0.8.20"
    
    @classmethod
    def from_env(cls) -> 'BenchmarkConfig':
        """Create configuration from environment variables"""
        return cls(
            llm=LLMConfig(
                model=os.getenv("LLM_MODEL", "gpt-4"),
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("LLM_BASE_URL"),
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.1")),
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", "4000"))
            ),
            blockchain=BlockchainConfig(
                rpc_url=os.getenv("RPC_URL"),
                private_key=os.getenv("PRIVATE_KEY"),
                sender_address=os.getenv("SENDER_ADDRESS"),
                chain_id=int(os.getenv("CHAIN_ID", "1"))
            ),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            timeout=int(os.getenv("TIMEOUT", "300")),
            output_dir=os.getenv("OUTPUT_DIR", "outputs"),
            solc_version=os.getenv("SOLC_VERSION", "0.8.20")
        )
    
    @classmethod
    def from_file(cls, config_path: str) -> 'BenchmarkConfig':
        """Create configuration from config file"""
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        return cls(
            llm=LLMConfig(**config_data["llm"]),
            blockchain=BlockchainConfig(**config_data["blockchain"]),
            max_retries=config_data.get("max_retries", 3),
            timeout=config_data.get("timeout", 300),
            output_dir=config_data.get("output_dir", "outputs"),
            solc_version=config_data.get("solc_version", "0.8.20")
        )
    
    def validate(self) -> None:
        """Validate configuration"""
        if not self.llm.api_key:
            raise ValueError("LLM API key is required")
        if not self.blockchain.rpc_url:
            raise ValueError("RPC URL is required")
        if not self.blockchain.private_key:
            raise ValueError("Private key is required")
        if not self.blockchain.sender_address:
            raise ValueError("Sender address is required")