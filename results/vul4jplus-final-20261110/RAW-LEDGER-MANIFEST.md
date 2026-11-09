# Raw ledger release asset

Release tag: `vul4jplus-paper-evidence-20261110`

Asset: `vulris-paper-log-analysis-20261110.zip`

- Size: 304,673,225 bytes
- SHA-256: `98a1b3420908f7dc0b34a505752865d8dc1cc074332984d811c77f12a95b8150`
- Entries: 17

## Members

### Criteria and mapping artifacts

- `criteria/ALL-MODEL-VUL4JPLUS-BINARY-ADJUDICATION-20261101.json`
- `criteria/ALL-API-RESPONSE-INTEGRITY-20261103.json`
- `criteria/result-20261023T090802Z.json`
- `criteria/paired-results-case172-corrected.json`

### Gemini ledgers

- `ledgers/gemini/b0/batch-ledger.sqlite3`
- `ledgers/gemini/p1/batch-ledger.sqlite3`

### GPT-6 Luna ledgers

- `ledgers/gpt6-luna-high/b0/batch-ledger.sqlite3`
- `ledgers/gpt6-luna-high/p1/batch-ledger.sqlite3`
- `ledgers/gpt6-luna-max/b0/batch-ledger.sqlite3`
- `ledgers/gpt6-luna-max/p1/batch-ledger.sqlite3`

### DeepSeek ledgers and correction overlays

- `ledgers/deepseek/b0-main/run-ledger.sqlite3`
- `ledgers/deepseek/b0-case057-input-correction/run-ledger.sqlite3`
- `ledgers/deepseek/b0-report-format-plus/run-ledger.sqlite3`
- `ledgers/deepseek/p1-main/run-ledger.sqlite3`
- `ledgers/deepseek/p1-case057-repair/run-ledger.sqlite3`
- `ledgers/deepseek/p1-format-retry/run-ledger.sqlite3`
- `ledgers/deepseek/p1-report-format-plus/run-ledger.sqlite3`

GPT-5.6 Luna ledgers are not included because that model family was excluded
from the final paper and comparative experiment.

## Credential screening

The archive was scanned before publication for Google, OpenAI, GitHub, AWS,
and Slack token formats and for PEM private-key markers. No API or account
credential signature was found. Twenty-five PEM markers occur only inside
public benchmark-source snippets, read-only tool responses, and source-search
arguments in the experiment messages; they are test fixtures, not runner
configuration credentials.
