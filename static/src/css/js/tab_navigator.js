/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { FormController } from "@web/views/form/form_controller";
import { useEffect } from "@odoo/owl";

const TAB_ORDER = [
    'tab_profile',
    'tab_trip',
    'tab_interests',
    'tab_itinerary',
    'tab_destination',
    'tab_reviews',
    'tab_map',
];

function switchTab(tabName) {
    const allLinks = document.querySelectorAll(".o_notebook .nav-link");

    // Method 1: match by aria-controls / data-bs-target / href / id
    for (const link of allLinks) {
        const attrs = [
            link.getAttribute("aria-controls") || "",
            link.getAttribute("data-bs-target") || "",
            link.getAttribute("href") || "",
            link.getAttribute("id") || "",
            link.getAttribute("data-target") || "",
        ];
        if (attrs.some(a => a.includes(tabName))) {
            link.click();
            return;
        }
    }

    // Method 2: fallback by index position
    const idx = TAB_ORDER.indexOf(tabName);
    if (idx !== -1 && allLinks[idx]) {
        allLinks[idx].click();
    }
}

window.goToTab = switchTab;

patch(FormController.prototype, {
    setup() {
        super.setup();

        // Your existing active_tab from context logic
        useEffect(() => {
            const activeTab =
                this.props?.context?.active_tab ||
                this.model?.root?.context?.active_tab ||
                this.env?.searchModel?.context?.active_tab;

            if (activeTab) {
                setTimeout(() => switchTab(activeTab), 300);
            }
        });

        // Attach click listeners to all [data-tab-target] buttons
        useEffect(() => {
            const buttons = document.querySelectorAll("[data-tab-target]");
            buttons.forEach(btn => {
                btn.addEventListener("click", (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    switchTab(btn.getAttribute("data-tab-target"));
                });
            });
        });
    },
});