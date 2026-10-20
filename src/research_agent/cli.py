import argparse
import sys

from research_agent.models import ResearchRequest
from research_agent.service import ConfigurationError, conduct_research
from research_agent.storage import initialize_database


def main() -> None:
    parser = argparse.ArgumentParser(description="Create a cited research report from web sources.")
    parser.add_argument("query", help="Research question or topic")
    parser.add_argument("--depth", choices=("basic", "advanced"), default="advanced")
    parser.add_argument("--max-results", type=int, default=None)
    args = parser.parse_args()
    try:
        initialize_database()
        request = ResearchRequest(
            query=args.query,
            depth=args.depth,
            **({"max_results": args.max_results} if args.max_results is not None else {}),
        )
        result = conduct_research(request)
    except (ConfigurationError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    print(result.report)
    print("\nSources:")
    for source in result.sources:
        print(f"[{source.id}] {source.title} — {source.url}")


if __name__ == "__main__":
    main()
