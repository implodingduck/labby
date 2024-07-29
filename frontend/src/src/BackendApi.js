class BackendApi {
    baseurl;

    constructor() {
        this.baseurl = 'http://localhost:8080'
    }

    async echo(question) {
        const resp = await fetch(`${this.baseurl}/echo`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({question: question})
        });
        return await resp.json();
    }

    async chat(question) {
        const resp = await fetch(`${this.baseurl}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({question: question})
        });
        return await resp.json();
    }
}

export { BackendApi }