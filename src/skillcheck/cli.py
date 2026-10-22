#!/usr/bin/env python3
import click
from rich.console import Console
console=Console()
@click.group()
def main(): pass
@main.command()
def check():
    console.print('[green]Valid[/green]')
if __name__=='__main__': main()
