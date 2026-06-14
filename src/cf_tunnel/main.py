from cf_tunnel.theme import console

def main():
    console.print("[bold text]Welcome to [primary]cf-tunnel[/primary][/bold text]")
    console.print("[success]✓ Setup complete.[/success]")
    console.print("[info]i Information:[/info] This project uses the Homebrew Neon color scheme.")
    console.print("[warning]⚠ Warning:[/warning] Experimental features enabled.")
    console.print("[danger]✖ Error:[/danger] Just kidding, no errors.")
    console.print("\n[muted]Debug output...[/muted]")

if __name__ == "__main__":
    main()
