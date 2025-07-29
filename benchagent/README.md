# BenchmarkAgent

An intelligent agent framework specialized for blockchain benchmarking. This framework can accept complex blockchain tasks, automatically decompose them into executable steps, generate Solidity contracts and Python scripts, and execute complete blockchain operation workflows.

## Core Features

- **Intelligent Task Decomposition**: Uses LLM to break down complex tasks into executable steps
- **Automatic Code Generation**: Automatically generates Solidity smart contracts and Python blockchain interaction scripts
- **Error Feedback Repair**: Automatically feeds error information back to LLM when execution fails, generating fixed code
- **Multi-round Retry Mechanism**: Supports configurable maximum retry attempts to improve task success rate
- **Complete Execution Environment**: Built-in Solidity compiler and Python execution environment
- **Detailed Logging**: Complete execution logs and result tracking

## Architecture Design

```
BenchmarkAgent
├── TaskManager (Task Management)
├── TaskPlanner (Task Planning & Decomposition)
├── StepExecutor (Step Executor)
│   ├── CodeGenerator (Code Generation)
│   ├── SolidityExecutor (Solidity Compilation & Deployment)
│   ├── PythonExecutor (Python Script Execution)
│   └── ErrorHandler (Error Feedback Loop)
└── ResultCollector (Result Collection & Validation)
```

## Installation and Configuration

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install OpenZeppelin contract library (if needed)
npm install @openzeppelin/contracts
```

### 2. Environment Configuration

Copy `.env.example` to `.env` and fill in your configuration:

```bash
cp .env.example .env
```

Edit the `.env` file:

```bash
# LLM configuration
OPENAI_API_KEY=your_openai_api_key_here
LLM_MODEL=gpt-4

# Blockchain configuration
RPC_URL=https://mainnet.infura.io/v3/your_project_id
PRIVATE_KEY=your_private_key_here
SENDER_ADDRESS=your_sender_address_here
CHAIN_ID=1
```

### 3. Configuration File

Alternatively, use configuration file approach by editing `config/config.json`:

```json
{
  "llm": {
    "model": "gpt-4",
    "api_key": "${OPENAI_API_KEY}",
    "temperature": 0.1,
    "max_tokens": 4000
  },
  "blockchain": {
    "rpc_url": "${RPC_URL}",
    "private_key": "${PRIVATE_KEY}",
    "sender_address": "${SENDER_ADDRESS}",
    "chain_id": 1
  }
}
```

## Usage

### Basic Usage

```bash
# Use environment variable configuration
python main.py --env --tasks config/tasks.json

# Use configuration file
python main.py --config config/config.json --tasks config/tasks.json

# Dry run mode (only validate configuration)
python main.py --env --dry-run
```

### Custom Tasks

Edit `config/tasks.json` to add your benchmark tasks:

```json
{
  "tasks": [
    {
      "id": "001",
      "description": "Deploy an ERC20 token contract with name 'TestToken', symbol 'TT', and total supply of 1000000 tokens",
      "type": "deployment",
      "max_retries": 3,
      "timeout": 300
    },
    {
      "id": "002",
      "description": "Deploy an ERC20 token and then transfer 1000 tokens to address 0x742d35Cc6634C0532925a3b8D4B329b36E6B23f8",
      "type": "multi_step",
      "max_retries": 3,
      "timeout": 600
    }
  ]
}
```

## Task Types

- **query**: Blockchain query operations
- **transaction**: Simple transaction operations  
- **deployment**: Smart contract deployment
- **multi_step**: Multi-step composite operations
- **defi**: DeFi protocol interactions

## Execution Flow

1. **Task Loading**: Load benchmark tasks from configuration file
2. **Task Planning**: LLM analyzes tasks and breaks them down into execution steps
3. **Code Generation**: Generate corresponding Solidity or Python code for each step
4. **Code Execution**: Compile and deploy contracts or execute Python scripts
5. **Error Handling**: When execution fails, feedback error information to LLM to regenerate code
6. **Result Collection**: Collect and analyze all execution results

## Output Results

After execution completes, results are saved in the `outputs/` directory:

```
outputs/
├── results/           # Task execution results
├── logs/             # Detailed execution logs  
├── task_001/         # Task-specific directory
├── contracts/        # Generated contract files
├── scripts/          # Generated script files
└── summary.json      # Execution summary
```

## Log Levels

Supported log levels: DEBUG, INFO, WARNING, ERROR

```bash
python main.py --env --log-level DEBUG
```

## Error Handling

The framework includes intelligent error handling mechanisms:

- **Compilation Errors**: Automatically feedback Solidity compilation errors to LLM for fixing
- **Runtime Errors**: Feedback Python script execution errors to LLM for regeneration
- **Transaction Failures**: Analyze blockchain transaction failure reasons and attempt fixes
- **Network Issues**: Automatically retry network-related operations

## Extension Development

### Adding New Executors

```python
from executors.base_executor import BaseExecutor

class CustomExecutor(BaseExecutor):
    def execute(self, code: str, step_id: str) -> Tuple[bool, Dict[str, Any]]:
        # Implement custom execution logic
        pass
```

### Custom Code Generator

```python
from core.code_generator import CodeGenerator

class CustomCodeGenerator(CodeGenerator):
    def _generate_custom_code(self, step, context, previous_error):
        # Implement custom code generation logic
        pass
```

## Notes

- Ensure sufficient ETH for gas fees
- Keep private keys secure, do not commit to version control
- Recommend using test networks for testing environment
- Consider increasing timeout configuration for large tasks

## License

MIT License