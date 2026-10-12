async function loadList() {

    const response = await fetch("api/list");

    const data = await response.json();

    const tbody = document.getElementById("lista");

    tbody.innerHTML = "";

    for (const item of data) {

        const tr = document.createElement("tr");

        if (item.teljesult) {
            tr.classList.add("done");
        }

        tr.innerHTML = `
            <td>
                <input
                    type="checkbox"
                    ${item.teljesult ? "checked" : ""}
                    onchange="toggleDone(
                        ${item.id},
                        this.checked
                    )"
                >
            </td>

            <td>${item.mit}</td>

            <td>${item.mennyit ?? ""}</td>

            <td>${item.mertekegyseg ?? ""}</td>

            <td>${item.honnan ?? ""}</td>

            <td>
                <button
                    class="danger small"
                    onclick="deleteItem(${item.id})"
                >
                    X
                </button>
            </td>
        `;

        tbody.appendChild(tr);
    }
}


async function addItem() {

    const mit =
        document.getElementById("mit").value.trim();

    const mennyit =
        document.getElementById("mennyit").value;

    const me =
        document.getElementById("me").value.trim();

    const honnan =
        document.getElementById("honnan").value.trim();


    if (!mit) {

        alert("A 'Mit?' mező kötelező.");

        return;
    }


    const body = {
        mit: mit,
        mennyit: mennyit
            ? Number(mennyit)
            : null,
        me: me || null,
        honnan: honnan || null
    };


    const response = await fetch(
        "api/add",
        {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify(body)
        }
    );


    if (!response.ok) {

        alert("Hiba történt a hozzáadásnál.");

        return;
    }


    document.getElementById("mit").value = "";
    document.getElementById("mennyit").value = "";
    document.getElementById("me").value = "";
    document.getElementById("honnan").value = "";

    await loadList();
}


async function toggleDone(id, checked) {

    const endpoint = checked
        ? `api/done-id/${id}`
        : `api/undone-id/${id}`;


    const response = await fetch(
        endpoint,
        {
            method: "POST"
        }
    );


    if (!response.ok) {

        alert("Hiba történt az állapot módosításánál.");
    }


    await loadList();
}


async function deleteItem(id) {

    if (!confirm("Biztosan törlöd ezt a tételt?")) {
        return;
    }


    const response = await fetch(
        `api/delete-id/${id}`,
        {
            method: "DELETE"
        }
    );


    if (!response.ok) {

        alert("Hiba történt a törlésnél.");
    }


    await loadList();
}


async function deleteAll() {

    if (!confirm(
        "Biztosan törlöd az összes tételt?"
    )) {
        return;
    }


    const response = await fetch(
        "api/delete-all",
        {
            method: "DELETE"
        }
    );


    if (!response.ok) {

        alert("Hiba történt.");
    }


    await loadList();
}


loadList();