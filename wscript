import os.path

top = '.'
out = 'build'

def options(ctx):
    ctx.load('pebble_sdk')

def configure(ctx):
    ctx.load('pebble_sdk')

def build(ctx):
    ctx.load('pebble_sdk')
    binaries = []
    cached_env = ctx.env
    for p in ctx.env.TARGET_PLATFORMS:
        ctx.set_env(ctx.all_envs[p])
        ctx.set_group(ctx.env.PLATFORM_NAME)
        app_elf = ctx.pebble_build_simple_app(
            sources=ctx.path.ant_glob('src/**/*.c'))
        binaries.append({'platform': p, 'app_elf': app_elf})
        ctx.set_env(cached_env)
    ctx.set_group('bundle')
    ctx.pebble_bundle(binaries=binaries)
