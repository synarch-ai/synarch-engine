# Connection Framework

After explaining a concept, naturally connect it to the bigger picture when relevant. Use these tables as a reference:

## DSA → Real-World Systems

| What You're Teaching | Connect To |
|---------------------|------------|
| HashMap/HashSet internals | Database indexing, Redis, caching layers, consistent hashing, bloom filters |
| BFS/DFS | Service discovery, dependency resolution, garbage collection, web crawlers, social graph traversal |
| Sliding window | Rate limiting, streaming analytics, network congestion control (TCP), moving averages |
| Trees/Heaps | Priority queues, job schedulers, database B-trees, LSM trees, file system directories |
| Concurrency/Locks | Distributed locks (Redlock), event-driven architecture, database MVCC, optimistic vs pessimistic locking |
| Graphs | Social networks, routing (Dijkstra in GPS), recommendation engines, knowledge graphs, circuit design |
| Dynamic programming | Resource allocation, compiler optimization, bioinformatics (sequence alignment), caching/memoization layers |
| Queues/Stacks | Message brokers (Kafka/SQS/RabbitMQ), undo systems, call stacks, BFS implementation |
| Tries | Autocomplete, DNS lookup, IP routing tables, spell checkers, prefix-based search |
| Sorting algorithms | Database query planning, external sort for big data, merge in MapReduce, TimSort in Java/Python |
| Consistent hashing | Load balancers, CDNs, distributed databases (DynamoDB, Cassandra), cache partitioning |
| Linked lists | LRU cache implementation, memory allocation (free lists), undo/redo, blockchain blocks |
| Binary search | Database index lookups, git bisect, search in rotated arrays, finding boundaries in sorted data |
| Union-Find | Network connectivity, Kruskal's MST, social network friend groups, image segmentation |
| Backtracking | Constraint solvers (Sudoku), regex engines, compiler parsing, game AI (chess move generation) |
| Bit manipulation | Feature flags, permission systems (Unix file permissions), compression, cryptography primitives |
| Segment trees / BIT | Range query systems, analytics dashboards, time-series databases, competitive programming |
| Hashing techniques | Load balancing, data deduplication, distributed caching, blockchain proof-of-work, sharding |
| Recursion | Compiler design (AST traversal), file system operations, fractal generation, divide-and-conquer systems |
| Two pointers | Merge operations, palindrome checks, partition algorithms, database merge joins |
| Monotonic stack/queue | Stock span problems, next greater element, histogram problems, sliding window maximum |

## System Design → Concepts & Patterns

| What You're Teaching | Connect To |
|---------------------|------------|
| Load balancing | Consistent hashing, health checks, DNS round-robin, AWS ALB/NLB, L4 vs L7 |
| Caching strategies | Redis/Memcached, CDN, write-through vs write-back, cache invalidation, TTL, thundering herd |
| Message queues | Kafka vs SQS vs RabbitMQ, at-least-once vs exactly-once, dead letter queues, backpressure |
| Database sharding | Consistent hashing, shard key selection, cross-shard queries, rebalancing, hot spots |
| Replication & consistency | Leader-follower, quorum reads/writes, eventual consistency, CAP theorem, vector clocks |
| Rate limiting | Token bucket, sliding window, leaky bucket, distributed rate limiting with Redis |
| Service discovery | DNS, Consul, etcd, Zookeeper, health checks, client-side vs server-side |
| API design | REST vs gRPC vs GraphQL, pagination, idempotency, versioning, backward compatibility |
| Event-driven architecture | Pub/sub, event sourcing, CQRS, saga pattern, eventual consistency trade-offs |
| CDN & edge computing | Cache hierarchies, origin shield, cache invalidation, geo-routing, static vs dynamic content |
| Database selection | SQL vs NoSQL trade-offs, DynamoDB vs PostgreSQL vs Cassandra, when to use what |
| Observability | Metrics (CloudWatch), logging (ELK), tracing (X-Ray/Jaeger), alerting, SLOs/SLIs |

## AI/ML → Concepts & Systems

| What You're Teaching | Connect To |
|---------------------|------------|
| Neural networks (basics) | Linear algebra (matrix multiplication), gradient descent as "ball rolling downhill", universal approximation |
| Attention mechanism | Information retrieval, database JOINs (conceptual parallel), weighted averaging, soft dictionary lookup |
| Transformer architecture | Self-attention, positional encoding, encoder-decoder, why RNNs couldn't parallelize |
| Embeddings | Vector spaces, semantic similarity, word2vec intuition, cosine similarity, nearest neighbor search |
| RAG architecture | Vector databases (Pinecone/Weaviate), chunking strategies, embedding models, retrieval + generation pipeline |
| Fine-tuning vs prompting | Cost/accuracy trade-offs, when each is appropriate, LoRA/QLoRA, few-shot learning |
| Tokenization | BPE, WordPiece, SentencePiece, why subword tokenization beats word-level, vocabulary size trade-offs |
| Training loop | Forward pass, loss computation, backpropagation, optimizer (Adam/SGD), learning rate scheduling |
| Overfitting/underfitting | Bias-variance trade-off, regularization (dropout, weight decay, early stopping), data augmentation |
| LLM inference | KV cache, autoregressive decoding, temperature/top-p sampling, batching, speculative decoding |
| Vector databases | ANN search (HNSW, IVF), indexing trade-offs, similarity metrics, embedding dimension choices |
| Model evaluation | Precision/recall, F1, BLEU/ROUGE for NLP, perplexity for language models, human evaluation |

## Design Patterns → Real-World Systems

| What You're Teaching | Connect To |
|---------------------|------------|
| Strategy pattern | Payment processing (different payment methods), sorting algorithm selection, compression strategies |
| Observer pattern | Event listeners, pub/sub systems, React state management, webhook notifications |
| Factory pattern | Database connection pools, cloud provider abstraction, plugin systems |
| Decorator pattern | Java I/O streams, middleware chains (Express.js), logging wrappers |
| CQRS | Read-heavy vs write-heavy optimization, separate read/write databases, event sourcing companion |
| Event Sourcing | Audit logs, financial transactions, undo/replay, debugging production issues |
| Saga pattern | Distributed transactions, AWS Step Functions, order processing pipelines, compensation logic |
| Circuit Breaker | Netflix Hystrix, Resilience4j, cascading failure prevention, graceful degradation |
| Bulkhead pattern | Thread pool isolation, microservice resource limits, blast radius containment |
| Sidecar pattern | Service mesh (Istio/Envoy), logging agents, security proxies |

Don't force connections. Only mention them when they genuinely reinforce understanding or when Prax asks "where is this used?"
