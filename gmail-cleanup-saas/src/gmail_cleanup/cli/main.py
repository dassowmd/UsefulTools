"""Gmail Cleanup CLI application."""

import logging
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.logging import RichHandler
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

from ..auth.oauth import CredentialsManager, AuthenticationError
from ..core.client import GmailClient
from ..core.processor import EmailProcessor
from ..rules.engine import RulesEngine, RuleValidationError
from ..rules.templates import RuleTemplates

# Configure rich console
console = Console()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--config-dir', help='Configuration directory path')
@click.pass_context
def app(ctx, verbose: bool, config_dir: Optional[str]):
    """Gmail Cleanup - Modern email management tool."""
    
    # Ensure context object exists
    ctx.ensure_object(dict)
    
    # Set logging level
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Setup configuration directory
    ctx.obj['config_dir'] = config_dir


# Authentication commands
@app.group()
def auth():
    """Authentication commands."""
    pass


@auth.command()
@click.option('--client-secrets', help='Path to client secrets JSON file')
@click.pass_context
def setup(ctx, client_secrets: Optional[str]):
    """Setup OAuth2 authentication."""
    try:
        credentials_manager = CredentialsManager(ctx.obj.get('config_dir'))
        
        if client_secrets:
            # Setup from file
            credentials_manager.setup_client_secrets(client_secrets)
            rprint(f"[green]✓[/green] Client secrets installed successfully")
        else:
            # Interactive setup
            console.print("Please follow these steps to setup authentication:")
            console.print("1. Go to https://console.developers.google.com")
            console.print("2. Create a new project or select existing")
            console.print("3. Enable Gmail API")
            console.print("4. Create OAuth2 credentials")
            console.print("5. Download the client secrets JSON file")
            
            secrets_path = click.prompt("Path to client secrets file")
            credentials_manager.setup_client_secrets(secrets_path)
            rprint(f"[green]✓[/green] Client secrets installed successfully")
        
    except Exception as e:
        rprint(f"[red]✗[/red] Setup failed: {e}")
        sys.exit(1)


@auth.command()
@click.pass_context
def login(ctx):
    """Login with Google OAuth2."""
    try:
        credentials_manager = CredentialsManager(ctx.obj.get('config_dir'))
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Authenticating...", total=None)
            
            success = credentials_manager.authenticate()
            
            progress.update(task, completed=True)
        
        if success:
            user_info = credentials_manager.get_user_info()
            rprint(f"[green]✓[/green] Successfully authenticated as {user_info.get('email')}")
        else:
            rprint("[red]✗[/red] Authentication failed")
            sys.exit(1)
    
    except AuthenticationError as e:
        rprint(f"[red]✗[/red] {e}")
        sys.exit(1)
    except Exception as e:
        rprint(f"[red]✗[/red] Login failed: {e}")
        sys.exit(1)


@auth.command()
@click.pass_context
def logout(ctx):
    """Logout and revoke credentials."""
    try:
        credentials_manager = CredentialsManager(ctx.obj.get('config_dir'))
        success = credentials_manager.logout()
        
        if success:
            rprint("[green]✓[/green] Successfully logged out")
        else:
            rprint("[yellow]⚠[/yellow] Logout may have failed")
    
    except Exception as e:
        rprint(f"[red]✗[/red] Logout failed: {e}")
        sys.exit(1)


@auth.command()
@click.pass_context
def status(ctx):
    """Check authentication status."""
    try:
        credentials_manager = CredentialsManager(ctx.obj.get('config_dir'))
        
        if credentials_manager.is_authenticated():
            user_info = credentials_manager.get_user_info()
            rprint(f"[green]✓[/green] Authenticated as {user_info.get('email')}")
            rprint(f"Messages: {user_info.get('messages_total', 'N/A')}")
            rprint(f"Threads: {user_info.get('threads_total', 'N/A')}")
        else:
            rprint("[red]✗[/red] Not authenticated")
            rprint("Run 'gmail-cleanup auth login' to authenticate")
            sys.exit(1)
    
    except Exception as e:
        rprint(f"[red]✗[/red] Status check failed: {e}")
        sys.exit(1)


# Rules commands
@app.group()
def rules():
    """Rules management commands."""
    pass


@rules.command()
@click.option('--file', '-f', help='Rules file path')
@click.pass_context
def list(ctx, file: Optional[str]):
    """List all rules."""
    try:
        rules_engine = RulesEngine(file)
        all_rules = rules_engine.get_rules()
        
        if not all_rules:
            rprint("[yellow]No rules found[/yellow]")
            return
        
        table = Table(title="Email Cleanup Rules")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Status", style="yellow")
        table.add_column("Priority", justify="right")
        table.add_column("Action", style="red")
        
        for rule in all_rules:
            status = "✓ Enabled" if rule.enabled else "✗ Disabled"
            table.add_row(
                rule.id[:8] + "...",
                rule.name,
                status,
                str(rule.priority),
                rule.action.type.value
            )
        
        console.print(table)
    
    except Exception as e:
        rprint(f"[red]✗[/red] Failed to list rules: {e}")
        sys.exit(1)


@rules.command()
@click.option('--template', '-t', help='Template ID to use')
@click.option('--file', '-f', help='Rules file path')
@click.pass_context
def create(ctx, template: Optional[str], file: Optional[str]):
    """Create a new rule."""
    try:
        rules_engine = RulesEngine(file)
        
        if template:
            # Create from template
            templates = {t['id']: t for t in RuleTemplates.get_all_templates()}
            
            if template not in templates:
                rprint(f"[red]✗[/red] Template '{template}' not found")
                available = ", ".join(templates.keys())
                rprint(f"Available templates: {available}")
                sys.exit(1)
            
            template_data = templates[template]
            
            # Get customizations
            rprint(f"Creating rule from template: {template_data['name']}")
            name = click.prompt("Rule name", default=template_data['name'])
            description = click.prompt("Description", default=template_data['description'])
            
            # Create rule
            rule = RuleTemplates.create_rule_from_template(
                template,
                name=name,
                description=description
            )
            
            rules_engine.add_rule(rule)
            
            if file:
                rules_engine.save_rules_to_file()
            
            rprint(f"[green]✓[/green] Created rule: {rule.name}")
        
        else:
            # Interactive creation
            rprint("[yellow]Interactive rule creation not yet implemented[/yellow]")
            rprint("Use --template option or web interface")
    
    except RuleValidationError as e:
        rprint(f"[red]✗[/red] Rule validation failed: {e}")
        sys.exit(1)
    except Exception as e:
        rprint(f"[red]✗[/red] Failed to create rule: {e}")
        sys.exit(1)


@rules.command()
@click.argument('rule_id')
@click.option('--file', '-f', help='Rules file path')
@click.pass_context
def delete(ctx, rule_id: str, file: Optional[str]):
    """Delete a rule."""
    try:
        rules_engine = RulesEngine(file)
        
        rule = rules_engine.get_rule(rule_id)
        if not rule:
            rprint(f"[red]✗[/red] Rule not found: {rule_id}")
            sys.exit(1)
        
        if click.confirm(f"Delete rule '{rule.name}'?"):
            success = rules_engine.remove_rule(rule_id)
            
            if success:
                if file:
                    rules_engine.save_rules_to_file()
                rprint(f"[green]✓[/green] Deleted rule: {rule.name}")
            else:
                rprint(f"[red]✗[/red] Failed to delete rule")
    
    except Exception as e:
        rprint(f"[red]✗[/red] Failed to delete rule: {e}")
        sys.exit(1)


@rules.command()
def templates():
    """List available rule templates."""
    try:
        templates = RuleTemplates.get_all_templates()
        categories = RuleTemplates.get_categories()
        
        for category in categories:
            category_templates = RuleTemplates.get_template_by_category(category)
            
            if category_templates:
                table = Table(title=f"{category.title()} Templates")
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="green")
                table.add_column("Risk", style="yellow")
                table.add_column("Description")
                
                for template in category_templates:
                    table.add_row(
                        template['id'],
                        template['name'],
                        template.get('risk_level', 'low'),
                        template['description'][:80] + "..." if len(template['description']) > 80 else template['description']
                    )
                
                console.print(table)
                console.print()
    
    except Exception as e:
        rprint(f"[red]✗[/red] Failed to list templates: {e}")
        sys.exit(1)


# Processing commands
@app.group()
def run():
    """Run email processing."""
    pass


@run.command()
@click.option('--rules-file', '-f', help='Rules file path')
@click.option('--dry-run', is_flag=True, help='Show what would be done without executing')
@click.option('--rule-id', help='Process specific rule only')
@click.option('--max-messages', type=int, help='Limit messages per rule')
@click.pass_context
def all(ctx, rules_file: Optional[str], dry_run: bool, rule_id: Optional[str], max_messages: Optional[int]):
    """Run all enabled rules."""
    try:
        # Check authentication
        credentials_manager = CredentialsManager(ctx.obj.get('config_dir'))
        
        if not credentials_manager.is_authenticated():
            rprint("[red]✗[/red] Not authenticated. Run 'gmail-cleanup auth login' first.")
            sys.exit(1)
        
        # Setup components
        auth_manager = credentials_manager.get_auth_manager()
        credentials = auth_manager.get_credentials()
        gmail_client = GmailClient(credentials)
        rules_engine = RulesEngine(rules_file)
        
        processor = EmailProcessor(gmail_client, rules_engine)
        
        # Add progress callback
        def progress_callback(stats):
            console.print(f"Processed: {stats.processed_messages}, Success: {stats.successful_operations}")
        
        processor.add_progress_callback(progress_callback)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(
                f"{'Analyzing' if dry_run else 'Processing'} rules...",
                total=None
            )
            
            if rule_id:
                # Process specific rule
                rule = rules_engine.get_rule(rule_id)
                if not rule:
                    rprint(f"[red]✗[/red] Rule not found: {rule_id}")
                    sys.exit(1)
                
                import asyncio
                result = asyncio.run(processor.process_rule(
                    rule=rule,
                    dry_run=dry_run,
                    max_messages=max_messages
                ))
                results = [result]
            else:
                # Process all rules
                import asyncio
                results = asyncio.run(processor.process_all_rules(
                    dry_run=dry_run,
                    max_messages_per_rule=max_messages
                ))
            
            progress.update(task, completed=True)
        
        # Display results
        table = Table(title=f"Processing Results ({'Dry Run' if dry_run else 'Executed'})")
        table.add_column("Rule", style="green")
        table.add_column("Matched", justify="right", style="cyan")
        table.add_column("Processed", justify="right", style="yellow")
        table.add_column("Succeeded", justify="right", style="green")
        table.add_column("Failed", justify="right", style="red")
        table.add_column("Duration", justify="right")
        
        total_matched = 0
        total_processed = 0
        total_succeeded = 0
        total_failed = 0
        
        for result in results:
            duration = f"{result.stats.duration:.2f}s" if result.stats.duration else "N/A"
            
            table.add_row(
                result.rule.name[:30] + "..." if len(result.rule.name) > 30 else result.rule.name,
                str(len(result.matched_messages)),
                str(result.batch_result.processed),
                str(result.batch_result.succeeded),
                str(result.batch_result.failed),
                duration
            )
            
            total_matched += len(result.matched_messages)
            total_processed += result.batch_result.processed
            total_succeeded += result.batch_result.succeeded
            total_failed += result.batch_result.failed
        
        console.print(table)
        
        # Summary
        rprint(f"\n[bold]Summary:[/bold]")
        rprint(f"Total matched: {total_matched}")
        rprint(f"Total processed: {total_processed}")
        rprint(f"Total succeeded: [green]{total_succeeded}[/green]")
        rprint(f"Total failed: [red]{total_failed}[/red]")
        
        if total_failed > 0:
            rprint(f"\n[yellow]⚠[/yellow] Some operations failed. Check logs for details.")
        
        # Cleanup
        processor.close()
    
    except AuthenticationError as e:
        rprint(f"[red]✗[/red] Authentication error: {e}")
        sys.exit(1)
    except Exception as e:
        rprint(f"[red]✗[/red] Processing failed: {e}")
        logger.exception("Processing error")
        sys.exit(1)


# Analysis commands
@app.group()
def analyze():
    """Analyze mailbox."""
    pass


@analyze.command()
@click.option('--max-messages', type=int, default=1000, help='Maximum messages to analyze')
@click.pass_context
def mailbox(ctx, max_messages: int):
    """Analyze mailbox and provide insights."""
    try:
        # Check authentication
        credentials_manager = CredentialsManager(ctx.obj.get('config_dir'))
        
        if not credentials_manager.is_authenticated():
            rprint("[red]✗[/red] Not authenticated. Run 'gmail-cleanup auth login' first.")
            sys.exit(1)
        
        # Setup components
        auth_manager = credentials_manager.get_auth_manager()
        credentials = auth_manager.get_credentials()
        gmail_client = GmailClient(credentials)
        rules_engine = RulesEngine()
        
        processor = EmailProcessor(gmail_client, rules_engine)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing mailbox...", total=None)
            
            import asyncio
            analysis = asyncio.run(processor.analyze_mailbox(max_messages=max_messages))
            
            progress.update(task, completed=True)
        
        # Display results
        rprint(f"[bold]Mailbox Analysis Results[/bold]")
        rprint(f"Analyzed messages: {analysis.get('total_messages', 0)}")
        rprint(f"Unread messages: {analysis.get('unread_messages', 0)}")
        rprint(f"Old messages (>1 year): {analysis.get('old_messages', 0)}")
        rprint(f"Unique senders: {analysis.get('unique_senders', 0)}")
        
        # Top sender domains
        top_senders = analysis.get('top_sender_domains', [])
        if top_senders:
            rprint(f"\n[bold]Top Sender Domains:[/bold]")
            
            table = Table()
            table.add_column("Domain", style="cyan")
            table.add_column("Count", justify="right", style="green")
            table.add_column("Percentage", justify="right", style="yellow")
            
            total_messages = analysis.get('total_messages', 1)
            for domain, count in top_senders[:10]:
                percentage = (count / total_messages) * 100
                table.add_row(domain, str(count), f"{percentage:.1f}%")
            
            console.print(table)
        
        # Suggestions
        suggestions = analysis.get('suggestions', [])
        if suggestions:
            rprint(f"\n[bold]Cleanup Suggestions:[/bold]")
            for i, suggestion in enumerate(suggestions, 1):
                rprint(f"{i}. {suggestion.get('title', 'Unknown')}")
                rprint(f"   {suggestion.get('description', '')}")
        
        # Cleanup
        processor.close()
    
    except Exception as e:
        rprint(f"[red]✗[/red] Analysis failed: {e}")
        logger.exception("Analysis error")
        sys.exit(1)


# Web server command
@app.command()
@click.option('--host', default='localhost', help='Host to bind to')
@click.option('--port', default=8000, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
def web(host: str, port: int, reload: bool):
    """Start web server."""
    try:
        import uvicorn
        from ..api.main import app as fastapi_app
        
        rprint(f"[green]Starting web server on http://{host}:{port}[/green]")
        rprint("Press Ctrl+C to stop")
        
        uvicorn.run(
            "gmail_cleanup.api.main:app",
            host=host,
            port=port,
            reload=reload,
            log_level="info"
        )
    
    except ImportError:
        rprint("[red]✗[/red] Web dependencies not installed. Install with: pip install gmail-cleanup[web]")
        sys.exit(1)
    except Exception as e:
        rprint(f"[red]✗[/red] Failed to start web server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    app()