# Release status — 13 November 2026

Source: https://github.com/sudip09-sys/Final_Project

Free live demo: https://attendly-sudip.onrender.com/

| Operation | Verified status |
|---|---|
| GitHub source publication | Complete |
| Application tests | 13 passed, including verified TLS configuration and temporary-storage notice |
| GitHub Actions on application commit `29a7c2fec9aa118a478ef7270c41377dd606eb23` | Success |
| Render Docker build and runtime | Live; deployment `dep-dbrfnr3bc2fs73cupg4g`, Free plan, Singapore |
| Public HTTPS health check and protected administrator login | Passed |
| Public manual attendance, duplicate prevention, CSV, close session, deletion, logout | Passed |
| Public desktop and mobile browser login | Passed; no page errors or page-wide horizontal overflow |
| Cloud storage | Temporary SQLite; records reset on restart. Warning displayed in app. |
| Persistent TiDB connection | Pending; account authorization was interrupted by the execution environment's network restriction |
| MySQL-compatible cloud database runtime and persistence after restart | Not verified |
| Real face enrollment and recognition | Previously passed locally using public test fixtures; no real participant data uploaded to the cloud smoke test |
| Physical camera hardware | Not tested |
| Report, presentation, research paper and recorded tutorials | Supplied in the separate submission ZIP; see README |

See [free deployment setup](Free_Deployment.md) for sign-in and the remaining persistent database connection. Do not use the temporary demo as durable attendance storage. The prototype has no liveness detection; use supervised, consent-based enrollment and a manual alternative.
