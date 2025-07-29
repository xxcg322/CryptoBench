## CryptoBench: A crypto-focus LLM Benchmark

CryptoBench is a comprehensive benchmark designed to assess the capabilities of large language models (LLMs) in understanding and applying cryptographic concepts, tools, and networks. Our goal is to create a robust evaluation framework that pushes the boundaries of AI in the crypto space.

### Leaderboard (updated on 2025.04.10)

**Important Note:** As AI models have evolved rapidly, the existing Q&A-based tests no longer provide sufficient differentiation between newer models, with scores becoming increasingly clustered at the high end. Since April 2025, we have discontinued running these traditional tests on new models and are transitioning to more challenging agent-driven real-world task benchmarks.

| Rank | Model                                          | Overall Score | Smart Contract Coding | Problem Solving | System Design | Calculation | Smart Contract Auditing | Knowledge |
| ---- | ---------------------------------------------- | ------------- | --------------------- | --------------- | ------------- | ----------- | ----------------------- | --------- |
| 1    | gemini-2.0-pro-exp-02-05                       | 92.14         | 94.08                 | 90.76           | 92.74         | 89.69       | 92.19                   | 92.88     |
| 2    | Gemini-2.5-pro-preview-03-25                   | 91.85         | 94.31                 | 91.24           | 91.69         | 90.50       | 92.02                   | 92.38     |
| 3    | claude-3-7-sonnet-20250219 (extended thinking) | 91.10         | 93.54                 | 90.84           | 91.54         | 87.69       | 91.74                   | 90.47     |
| 4    | DeepSeek-R1                                    | 90.99         | 93.00                 | 91.62           | 91.78         | 86.44       | 89.83                   | 91.17     |
| 5    | o3-mini-high                                   | 90.91         | 93.69                 | 90.58           | 91.47         | 88.88       | 91.45                   | 89.58     |
| 6    | Grok-3-beta                                    | 90.66         | 92.92                 | 90.56           | 90.72         | 88.06       | 91.02                   | 90.58     |
| 7    | claude-3-7-sonnet-20250219                     | 89.97         | 93.62                 | 90.27           | 90.62         | 84.44       | 90.64                   | 88.78     |
| 8    | o3-mini                                        | 89.86         | 93.31                 | 90.04           | 90.32         | 88.56       | 89.57                   | 88.47     |
| 9    | Grok-3-mini-beta                               | 89.53         | 93.15                 | 89.60           | 89.65         | 83.56       | 90.07                   | 89.90     |
| 10   | Qwen-Max-2025-01-25                            | 89.23         | 92.38                 | 88.64           | 89.14         | 88.88       | 90.79                   | 87.53     |
| 11   | claude-3-5-sonnet-20241022                     | 88.64         | 92.62                 | 88.51           | 89.24         | 86.50       | 88.57                   | 87.33     |
| 12   | gemini-2.0-flash-thinking-exp-01-21            | 88.11         | 91.15                 | 86.60           | 87.73         | 85.25       | 89.86                   | 88.85     |
| 13   | o1-preview                                     | 87.73         | 92.15                 | 85.56           | 87.69         | 83.69       | 90.67                   | 87.35     |
| 14   | o1-mini                                        | 87.58         | 92.85                 | 87.87           | 88.38         | 79.62       | 89.86                   | 84.85     |
| 15   | deepseek/deepseek-chat-v3-0324                 | 87.02         | 90.85                 | 87.11           | 86.59         | 83.00       | 88.52                   | 86.47     |
| 16   | glm-4-plus                                     | 86.68         | 89.31                 | 86.98           | 87.54         | 86.00       | 85.64                   | 85.28     |
| 17   | claude-3-5-sonnet-20240620                     | 86.32         | 91.92                 | 86.09           | 86.91         | 83.12       | 86.74                   | 84.50     |
| 18   | DeepSeek-V3                                    | 85.54         | 89.62                 | 85.47           | 84.73         | 80.75       | 88.69                   | 84.40     |
| 19   | Qwen2.5-72B-Instruct                           | 84.83         | 90.31                 | 84.68           | 86.97         | 81.38       | 83.12                   | 82.50     |
| 20   | gpt-4-turbo-2024-04-09                         | 84.65         | 86.77                 | 84.58           | 85.11         | 80.62       | 84.93                   | 84.53     |
| 21   | gpt-4o-2024-08-06                              | 84.63         | 86.15                 | 84.49           | 85.96         | 81.62       | 83.19                   | 84.53     |
| 22   | DeepSeek-V2.5                                  | 84.53         | 87.15                 | 85.36           | 86.05         | 80.12       | 83.88                   | 82.35     |
| 23   | Meta-Llama-3.1-405B-Instruct                   | 83.90         | 83.15                 | 85.29           | 86.50         | 82.38       | 78.52                   | 84.00     |
| 24   | claude-3-opus-20240229                         | 83.82         | 87.85                 | 83.44           | 85.57         | 81.06       | 82.36                   | 82.33     |
| 25   | gpt-4o-mini-2024-07-18                         | 83.22         | 87.69                 | 84.20           | 83.99         | 74.94       | 83.88                   | 81.88     |
| 26   | Meta-Llama-3.1-70B-Instruct                    | 83.05         | 83.62                 | 84.87           | 85.80         | 79.44       | 77.45                   | 83.05     |
| 27   | Llama-4-Maverick-17B-128E-Instruct-FP8         | 82.58         | 81.08                 | 84.16           | 85.14         | 81.19       | 75.21                   | 84.88     |
| 28   | gemini-1.5-pro                                 | 82.11         | 65.23                 | 84.36           | 84.70         | 82.12       | 81.19                   | 81.22     |
| 29   | gemma-2-27b-it                                 | 81.12         | 84.00                 | 82.38           | 84.31         | 74.38       | 77.60                   | 79.28     |
| 30   | mistral-nemo-12b-instruct-2407                 | 80.87         | 78.23                 | 82.62           | 84.85         | 75.00       | 76.00                   | 79.85     |
| 31   | claude-3-haiku-20240307                        | 80.56         | 82.54                 | 81.40           | 82.46         | 78.31       | 78.55                   | 78.45     |
| 32   | gemini-1.5-flash                               | 80.30         | 85.23                 | 81.76           | 82.77         | 76.69       | 75.62                   | 78.83     |
| 33   | Llama-4-Scout-17B-16E-Instruct                 | 79.66         | 71.08                 | 81.73           | 85.50         | 78.25       | 68.24                   | 81.88     |
| 34   | Mixtral-8x7B-Instruct-v0.1                     | 78.47         | 75.69                 | 81.87           | 81.68         | 71.50       | 71.29                   | 79.95     |
| 35   | Qwen2-Math-72B-Instruct                        | 77.98         | 60.92                 | 81.93           | 82.34         | 83.06       | 71.71                   | 75.58     |
| 36   | Meta-Llama-3.1-8B-Instruct                     | 77.30         | 74.31                 | 79.56           | 83.11         | 75.00       | 66.79                   | 76.95     |
| 37   | gemma-2-9b-it                                  | 76.54         | 80.23                 | 78.02           | 78.92         | 70.19       | 72.55                   | 76.03     |
| 38   | gpt-3.5-turbo-0125                             | 72.83         | 78.23                 | 73.84           | 75.43         | 65.50       | 70.07                   | 70.92     |
| 39   | phi3-14b-medium-128k-instruct                  | 71.68         | 64.92                 | 74.60           | 75.96         | 70.25       | 62.38                   | 73.03     |
| 40   | llama3.2:3b-instruct-q8_0                      | 70.27         | 69.77                 | 70.78           | 76.93         | 60.69       | 63.64                   | 68.33     |
| 41   | nous-hermes2:10.7b-solar-fp16                  | 70.20         | 65.08                 | 71.04           | 76.31         | 57.56       | 67.57                   | 67.40     |

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
