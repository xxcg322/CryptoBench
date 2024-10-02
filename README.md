## CryptoBench: A crypto-focus LLM Benchmark

CryptoBench is a comprehensive benchmark designed to assess the capabilities of large language models (LLMs) in understanding and applying cryptographic concepts, tools, and networks. Our goal is to create a robust evaluation framework that pushes the boundaries of AI in the crypto space.

### Leaderboard (updated on 2024.10.02)

| Rank | Model                          | Overall Score | coding | problem solving | system design | calculation | auditing | knowledge |
| ---- | ------------------------------ | ------------- | ------ | --------------- | ------------- | ----------- | -------- | --------- |
| 1    | o1-preview                     | 87.85         | 92.15  | 85.56           | 87.69         | 83.69       | 90.67    | 87.35     |
| 2    | o1-mini                        | 87.24         | 92.85  | 87.87           | 88.38         | 79.62       | 89.86    | 84.85     |
| 3    | claude-3-5-sonnet-20240620     | 85.65         | 89.85  | 84.69           | 86.54         | 82.25       | 86.29    | 84.28     |
| 4    | Qwen2.5-72B-Instruct           | 84.83         | 90.31  | 84.68           | 86.97         | 81.38       | 83.12    | 82.5      |
| 5    | gpt-4-turbo-2024-04-09         | 84.42         | 86.77  | 84.58           | 85.11         | 80.62       | 84.93    | 84.53     |
| 6    | gpt-4o-2024-08-06              | 84.32         | 86.15  | 84.49           | 85.96         | 81.62       | 83.19    | 84.53     |
| 7    | DeepSeek-V2.5                  | 84.15         | 87.15  | 85.36           | 86.05         | 80.12       | 83.88    | 82.35     |
| 8    | claude-3-opus-20240229         | 83.77         | 87.85  | 83.44           | 85.57         | 81.06       | 82.36    | 82.33     |
| 9    | Meta-Llama-3.1-405B-Instruct   | 83.31         | 83.15  | 85.29           | 86.5          | 82.38       | 78.52    | 84.0      |
| 10   | gpt-4o-mini-2024-07-18         | 82.76         | 87.69  | 84.2            | 83.99         | 74.94       | 83.88    | 81.88     |
| 11   | Meta-Llama-3.1-70B-Instruct    | 82.37         | 83.62  | 84.87           | 85.8          | 79.44       | 77.45    | 83.05     |
| 12   | gemma-2-27b-it                 | 80.33         | 84.0   | 82.38           | 84.31         | 74.38       | 77.6     | 79.28     |
| 13   | claude-3-haiku-20240307        | 80.29         | 82.54  | 81.4            | 82.46         | 78.31       | 78.55    | 78.45     |
| 14   | gemini-1.5-flash               | 80.15         | 85.23  | 81.76           | 82.77         | 76.69       | 75.62    | 78.83     |
| 15   | gemini-1.5-pro                 | 79.8          | 65.23  | 84.36           | 84.7          | 82.12       | 81.19    | 81.22     |
| 16   | mistral-nemo-12b-instruct-2407 | 79.42         | 78.23  | 82.62           | 84.85         | 75.0        | 76.0     | 79.85     |
| 17   | Mixtral-8x7B-Instruct-v0.1     | 77.0          | 75.69  | 81.87           | 81.68         | 71.5        | 71.29    | 79.95     |
| 18   | gemma-2-9b-it                  | 75.99         | 80.23  | 78.02           | 78.92         | 70.19       | 72.55    | 76.03     |
| 19   | Meta-Llama-3.1-8B-Instruct     | 75.95         | 74.31  | 79.56           | 83.11         | 75.0        | 66.79    | 76.95     |
| 20   | Qwen2-Math-72B-Instruct        | 75.92         | 60.92  | 81.93           | 82.34         | 83.06       | 71.71    | 75.58     |
| 21   | gpt-3.5-turbo-0125             | 72.33         | 78.23  | 73.84           | 75.43         | 65.5        | 70.07    | 70.92     |
| 22   | phi3-14b-medium-128k-instruct  | 70.19         | 64.92  | 74.6            | 75.96         | 70.25       | 62.38    | 73.03     |
| 23   | llama3.2:3b-instruct-q8_0      | 68.36         | 69.77  | 70.78           | 76.93         | 60.69       | 63.64    | 68.33     |
| 24   | nous-hermes2:10.7b-solar-fp16  | 67.49         | 65.08  | 71.04           | 76.31         | 57.56       | 67.57    | 67.4      |

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



## Future Directions

1. Agent Framework Development
   - Create a crypto-native framework for real-world blockchain interactions
   - Enable testing on test networks and live environments
2. Knowledge Graph Construction
   - Comprehensive mapping of the cryptography domain
   - Will inform future dataset construction and benchmark refinement
3. Data and Collaborative Expansion
   - CryptoBench is envisioned as a collective effort, current dataset is still early and more contribution is need.
   - We welcome contributions from the wider crypto and AI communities

## Current Status

All current work should be viewed as a early version. We are actively working towards building a robust, comprehensive benchmark that covers all aspects of the cryptography field.

## How to Contribute

We welcome contributions from individuals and teams across the crypto and AI landscapes. Whether you're an expert in cryptography, blockchain technology, or AI, your insights can help shape the future of CryptoBench.

Please refer to our [contribution guidelines](https://cryptobench.org/contribute) for detailed instructions on how to get involved.

## Community and Resources

- Join our [Discord server](https://discord.gg/cryptobench) for discussions and updates
- Follow us on [Twitter](https://twitter.com/cryptobench) for the latest news

## License

This project is licensed under the Creative Commons Attribution 4.0 International License (CC BY 4.0). See the [LICENSE](LICENSE) file for details.

## Contact

For inquiries, please email us at [contact@cryptobench.org](mailto:contact@cryptobench.org)

------

CryptoBench is continuously evolving with the rapidly advancing fields of cryptography and artificial intelligence. Join us in pushing the boundaries of what's possible at the intersection of these transformative technologies.
