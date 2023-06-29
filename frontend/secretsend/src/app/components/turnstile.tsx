import {Box} from '@mantine/core'

export default function Turnstile() {
    const sitekey = process.env.TURNSTYLE_SITEKEY;

    return (
        <Box>
            <div
                class="cf-turnstile"
                data-sitekey={ sitekey }
                data-callback="javascriptCallback">
            </div>
        </Box>
    )
}
