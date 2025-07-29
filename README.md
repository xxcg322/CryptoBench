## CryptoBench: A crypto-focus LLM Benchmark

CryptoBench is a comprehensive benchmark designed to assess the capabilities of large language models (LLMs) in understanding and applying cryptographic concepts, tools, and networks. Our goal is to create a robust evaluation framework that pushes the boundaries of AI in the crypto space.

### Leaderboard (updated on 2025.04.10)

**Important Note:** As AI models have evolved rapidly, the existing Q&A-based tests no longer provide sufficient differentiation between newer models, with scores becoming increasingly clustered at the high end. Since April 2025, we have discontinued running these traditional tests on new models and are transitioning to more challenging agent-driven real-world task benchmarks.

| Rank | Model                          | Overall Score | Smart Contract Coding | Problem Solving | System Design | Calculation | Smart Contract Auditing | Knowledge |
| ---- | ------------------------------ | ------------- | --------------------- | --------------- | ------------- | ----------- | ----------------------- | --------- |
| 1    | gemini-2.0-pro-exp-02-05       | 92.14         | 94.08                 | 90.76           | 92.74         | 89.69       | 92.19                   | 92.88     |
| 2    | Gemini-2.5-pro-preview-03-25   | 91.85         | 94.31                 | 91.24           | 91.69         | 90.50       | 92.02                   | 92.38     |
| 3    | claude-3-7-sonnet-20250219 (extended thinking) | 91.10 | 93.54         | 90.84           | 91.54         | 87.69       | 91.74                   | 90.47     |
| 4    | DeepSeek-R1                    | 90.99         | 93.00                 | 91.62           | 91.78         | 86.44       | 89.83                   | 91.17     |
| 5    | o3-mini-high                   | 90.91         | 93.69                 | 90.58           | 91.47         | 88.88       | 91.45                   | 89.58     |
| 6    | Grok-3-beta                    | 90.66         | 92.92                 | 90.56           | 90.72         | 88.06       | 91.02                   | 90.58     |
| 7    | claude-3-7-sonnet-20250219     | 89.97         | 93.62                 | 90.27           | 90.62         | 84.44       | 90.64                   | 88.78     |
| 8    | o3-mini                        | 89.86         | 93.31                 | 90.04           | 90.32         | 88.56       | 89.57                   | 88.47     |
| 9    | Grok-3-mini-beta               | 89.53         | 93.15                 | 89.60           | 89.65         | 83.56       | 90.07                   | 89.90     |
| 10   | Qwen-Max-2025-01-25            | 89.23         | 92.38                 | 88.64           | 89.14         | 88.88       | 90.79                   | 87.53     |

For detailed leaderboards on different topics, please visit our [comprehensive results page](https://github.com/xxcg322/CryptoBench/blob/main/Leaderboards.md).

## Project Components

1. Question Datasets
   - Task Dataset: 230 complex tasks covering cryptography, blockchain, cryptocurrencies, DeFi/Dapps, consensus mechanisms, smart contract understanding and auditing, smart contract code generation, scenario simulations, and Autonomous Agent capabilities based on crypto networks.
   - MVP Dataset: 727 multiple-choice questions for rapid LLM evaluation. (Note: This dataset is used only for initial concept demonstration due to its limitations in assessing LLMs' differential capabilities and is not included in the final problem set.)
2. Crypto Graph
   - Over 400 sub-domains and 1,300 knowledge areas
   - Covers cryptography fundamentals, smart contracts, tokenomics, DAOs, and governance
   - Focuses on real-world applications of AI agents in blockchain technology
3. Automated Testing Framework
   - Currently implemented for the MVP Dataset
   - Ongoing development for the Task Dataset
4. Crypto Agent Framework (Developing)
   - Crypto-native framework for autonomous agent to perform crypto-related tasks.


## Future Directions: From Q&A to Agent-Driven Real-World Tasks

CryptoBench is evolving beyond traditional Q&A benchmarks. We are transitioning to a more sophisticated evaluation framework where AI agents perform actual crypto-world tasks. 

### 🚀 BenchmarkAgent Framework (POC Available)

We have developed a proof-of-concept agent framework that demonstrates this new approach. The **[BenchmarkAgent](./benchagent/)** is a specialized intelligent agent framework for blockchain benchmarking that:

- **Automatically decomposes complex blockchain tasks** into executable steps using LLM
- **Generates Solidity contracts and Python scripts** for blockchain interactions
- **Executes complete blockchain workflows** with error feedback and retry mechanisms
- **Tests real-world scenarios** including DeFi protocols, NFT operations, and DAO governance


Key features:
- 🤖 LLM-driven task planning and code generation
- 🔄 Intelligent error feedback loop for code improvement
- 📊 Comprehensive execution logging and result tracking
- 🧪 10 progressive test tasks from simple queries to complex DeFi interactions

[Learn more about BenchmarkAgent →](./benchagent/README.md)

### Why This Transition?

- **Limited Differentiation**: Current Q&A tests no longer effectively differentiate between advanced models
- **Real-World Relevance**: Agent-driven tasks better reflect actual crypto development scenarios
- **Dynamic Challenges**: Real tasks require understanding complex interactions between smart contracts, protocols, and networks

### What's Next?

1. **Agent Framework Enhancement**
   - Building a robust crypto-native agent framework for real-world blockchain interactions
   - Enabling comprehensive testing on test networks and live environments

2. **New Dataset Construction**
   - Developing tasks that require actual blockchain interaction
   - Creating challenges that test understanding of DeFi protocols, smart contract deployment, and security auditing in practice

3. **Community Collaboration**
   - We welcome contributions from the crypto and AI communities
   - Help us define the next generation of crypto AI benchmarks



## Current Status

All current work should be viewed as a early version. We are actively working towards building a robust, comprehensive benchmark that covers all aspects of the cryptography field.

## How to Contribute

We welcome contributions from individuals and teams across the crypto and AI landscapes. Whether you're an expert in cryptography, blockchain technology, or AI, your insights can help shape the future of CryptoBench.

Please refer to our [contribution guidelines](https://cryptobench.org/contribute) for detailed instructions on how to get involved.

## Community and Resources

- Follow us on [Twitter](https://twitter.com/cryptobench) for the latest news

## License

This project is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0). See the [LICENSE](LICENSE) file for details.

## Contact

For inquiries, please email us at [contact@cryptobench.org](mailto:contact@cryptobench.org)

------

CryptoBench is continuously evolving with the rapidly advancing fields of cryptography and artificial intelligence. Join us in pushing the boundaries of what's possible at the intersection of these transformative technologies.
