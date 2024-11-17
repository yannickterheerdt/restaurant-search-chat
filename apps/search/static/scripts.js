$(document).ready(function () {
    // Fetch filter data when the page loads
    $.getJSON("/get_filter_options", function (data) {
        const { meal_type, district, restaurant_type, price_level } = data;

        // Populate filter checkboxes and hide extras
        populateFilterOptions("#meal_type_options", meal_type, "meal_type");
        populateFilterOptions("#district_options", district, "district");
        populateFilterOptions("#restaurant_type_options", restaurant_type, "restaurant_type");
        populateFilterOptions("#price_level_options", price_level, "price_level");
    }).fail(function () {
        alert("Failed to load filter options. Please try again.");
    });

    // Function to populate filter options and initially hide extra options beyond 5
    function populateFilterOptions(containerId, options, filterName) {
        const $container = $(containerId);
        const $toggleButton = $container.next(".toggle-options");

        options.forEach((option, index) => {
            const displayClass = index >= 5 ? "extra-option d-none" : "";
            $container.append(`
                <div class="form-check ${displayClass}">
                    <input type="checkbox" class="form-check-input" id="${containerId.slice(1)}_${option}" value="${option}" name="${filterName}">
                    <label class="form-check-label" for="${containerId.slice(1)}_${option}">${option}</label>
                </div>
            `);
        });

        if (options.length > 5) {
            $toggleButton.removeClass("d-none");
        }
    }

    // Toggle display of extra options and change button text
    $(".toggle-options").on("click", function () {
        const $button = $(this);
        const target = $button.data("target");
        const toggleText = $button.data("toggle-text");

        // Show/hide extra options in the filter group
        $(`${target} .extra-option`).toggleClass("d-none");

        // Toggle button text between "Meer" and "Minder"
        $button.text($button.text() === "Meer" ? toggleText : "Meer");
    });

    // Toggle filter section visibility with animation and change icon direction
    $("#toggle-filters").on("click", function () {
        $("#filter-section").slideToggle(300);
        $(this).find("i").toggleClass("fa-angle-double-right fa-angle-double-down");
    });

    // Submit form and gather filter data
    $("#question-form").on("submit", function (event) {
        event.preventDefault();
        const question = $("#question").val();

        // Gather selected filter values for each category
        const mealTypes = $("input[name='meal_type']:checked").map(function () {
            return this.value;
        }).get();
        const districts = $("input[name='district']:checked").map(function () {
            return this.value;
        }).get();
        const restaurantTypes = $("input[name='restaurant_type']:checked").map(function () {
            return this.value;
        }).get();
        const priceLevels = $("input[name='price_level']:checked").map(function () {
            return this.value;
        }).get();

        // Show loading spinner and clear previous results
        $("#loading-spinner").show();
        $("#recommendations").empty();

        $.post({
            url: "/get_filtered_names",
            contentType: "application/json",
            data: JSON.stringify({
                meal_type: mealTypes,
                district: districts,
                restaurant_type: restaurantTypes,
                price_level: priceLevels
            }),
            success: function (nameData) {
                const names = nameData.names;

                // Step 2: POST request to `/query` with names and question to get detailed recommendations
                $.post({
                    url: "/query",
                    contentType: "application/json",
                    data: JSON.stringify({
                        question: question,
                        names: names
                    }),
                    success: function (data) {
                        $("#loading-spinner").hide();
                        data.forEach(restaurant => {
                            const {
                                name,
                                summary,
                                image_url,
                                website_url = '',
                                instagram_url = '',
                                restaurant_type = '',
                                district = '',
                                meal_type = '',
                                price_level = ''
                            } = restaurant;

                            const card = `
                                <div class="card my-3 card-custom">
                                    <div class="row no-gutters h-100">
                                        <div class="col-md-8">
                                            <div class="card-body d-flex flex-column">
                                                <h5 class="card-title">${name}</h5>
                                                <p class="card-text">${summary}</p>
                                            </div>
                                        </div>
                                        <div class="col-md-4 position-relative h-100">
                                            <img src="${image_url}" class="card-img" alt="${name} image">
                                            <div class="info-overlay">
                                                <p><strong>Type:</strong> ${restaurant_type || "Niet beschikbaar"}</p>
                                                <p><strong>District:</strong> ${district || "Niet beschikbaar"}</p>
                                                <p><strong>Maaltijdtype:</strong> ${meal_type || "Niet beschikbaar"}</p>
                                                <p><strong>Prijsniveau:</strong> ${price_level || "Niet beschikbaar"}</p>
                                                <div class="mt-3">
                                                    ${website_url ? `<a href="${website_url}" target="_blank" class="icon-custom mr-3"><i class="fas fa-globe fa-lg"></i></a>` : ""}
                                                    ${instagram_url ? `<a href="${instagram_url}" target="_blank" class="icon-custom"><i class="fab fa-instagram fa-lg"></i></a>` : ""}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>`;
                            $("#recommendations").append(card);
                        });
                    },
                    error: function () {
                        $("#loading-spinner").hide();
                        alert("Failed to fetch recommendations. Please try again.");
                    }
                });
            },
            error: function () {
                $("#loading-spinner").hide();
                alert("Failed to fetch filtered names. Please try again.");
            }
        });
    });
});
