export function getInstructions(initialState) {
    return fetch("/api/evaluate-execution-plan", {
        method: "post",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(initialState)
    }).then(response => response.json())
}
