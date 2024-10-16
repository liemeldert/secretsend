// This exists because the NEXT_PUBLIC_ prefix isn't reliable
// also can't be changed live, so this is a workaround
export interface ApiResponse {
    backend_url: string;
    turnstyle_siteid: string;
  }

export async function GET(request: Request) {
    const data: ApiResponse = {
        backend_url: process.env.BACKEND_URL || 'http://localhost:8000',
        turnstyle_siteid: process.env.TURNSTYLE_SITEID || '1x00000000000000000000AA',
      };
    return new Response(JSON.stringify(data), {
        headers: {
            'content-type': 'application/json;charset=UTF-8',
        },
    });
}