async function loadList() {

    const response = await fetch("api/list");

    const data = await response.json();

    const container = document.getElementById("lista");

    container.innerHTML = "";


    if (data.length === 0) {

        container.innerHTML = `
            <div class="empty">
                A bevásárlólista üres.
            </div>
        `;

        return;
    }


    const groups = {};


    for (const item of data) {

        const store = item.honnan || "Egyéb";

        if (!groups[store]) {
            groups[store] = [];
        }

        groups[store].push(item);
    }


    for (const store of Object.keys(groups)) {

        const section = document.createElement("section");

        section.className = "store-section";


        const title = document.createElement("h2");

        title.textContent = store;

        section.appendChild(title);


        for (const item of groups[store]) {

            const row = document.createElement("div");

            row.className = "item-row";

            if (item.teljesult) {
                row.classList.add("done");
            }


            let quantity = "";

            if (item.mennyit !== null) {

                quantity += item.mennyit;
            }

            if (item.mertekegyseg) {

                if (quantity) {
                    quantity += " ";
                }

                quantity += item.mertekegyseg;
            }


            row.innerHTML = `
                <label class="item-main">

                    <input
                        type="checkbox"
                        ${item.teljesult ? "checked" : ""}
                        onchange="toggleDone(
                            ${item.id},
                            this.checked
                        )"
                    >

                    <span class="checkmark"></span>

                    <span class="item-name">
                        ${escapeHtml(item.mit)}
                    </span>

                </label>

                <span class="quantity">
                    ${escapeHtml(quantity)}
                </span>
            `;


            section.appendChild(row);
        }


        container.appendChild(section);
    }
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

        alert("Nem sikerült módosítani a tételt.");

        return;
    }


    await loadList();
}


function escapeHtml(value) {

    const div = document.createElement("div");

    div.textContent = value ?? "";

    return div.innerHTML;
}


loadList();