<script>
    import Footer from "$lib/components/Footer.svelte";
    import MenuIcon from "$lib/components/MenuIcon.svelte";

    let pageTitle = "Stupid Investor Bot";
</script>

<div class="navbar bg-neutral text-neutral-content">
    <div class="navbar-start">
        <div class="dropdown">
            <div tabindex="0" role="button" class="btn btn-ghost btn-circle">
                <MenuIcon />
            </div>
            <ul
                class="menu menu-sm dropdown-content bg-neutral text-neutral-content rounded-box z-[1] mt-3 w-52 p-2 shadow"
            >
                <li><a href="/">Home</a></li>
                <li><a href="/market-analysis">Market Analysis</a></li>
            </ul>
        </div>
    </div>
    <div class="navbar-center"><a href="/">Stupid Investor Bot</a></div>
    <div class="navbar-end"></div>
</div>
<slot />
<Footer />
