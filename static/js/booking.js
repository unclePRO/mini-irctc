// ============================================================================
// Dynamic Passenger Management & Live Fare Preview (Vanilla JavaScript)
// ============================================================================

document.addEventListener('DOMContentLoaded', function () {
    const passengersContainer = document.getElementById('passengers-container');
    const addPassengerBtn = document.getElementById('add-passenger-btn');
    const passengerCountSpan = document.getElementById('passenger-count');
    const totalFareDisplay = document.getElementById('total-fare-display');
    const baseFareInput = document.getElementById('base-fare-value');

    const MAX_PASSENGERS = 6;
    const baseFare = baseFareInput ? parseFloat(baseFareInput.value) || 0 : 0;

    function updateCalculations() {
        const rows = passengersContainer.querySelectorAll('.passenger-row');
        const count = rows.length;

        if (passengerCountSpan) {
            passengerCountSpan.textContent = count;
        }

        if (totalFareDisplay) {
            const calculatedTotal = (count * baseFare).toFixed(2);
            totalFareDisplay.textContent = '₹' + calculatedTotal;
        }

        // Enable or disable the Add button based on max limit
        if (addPassengerBtn) {
            if (count >= MAX_PASSENGERS) {
                addPassengerBtn.disabled = true;
                addPassengerBtn.classList.add('opacity-50', 'cursor-not-allowed');
            } else {
                addPassengerBtn.disabled = false;
                addPassengerBtn.classList.remove('opacity-50', 'cursor-not-allowed');
            }
        }

        // Renumber passenger sequence labels
        rows.forEach((row, index) => {
            const title = row.querySelector('.passenger-num');
            if (title) {
                title.textContent = `Passenger ${index + 1}`;
            }

            const removeBtn = row.querySelector('.remove-passenger-btn');
            if (removeBtn) {
                // Cannot remove the first passenger if only 1 remains
                if (count === 1) {
                    removeBtn.classList.add('hidden');
                } else {
                    removeBtn.classList.remove('hidden');
                }
            }
        });
    }

    if (addPassengerBtn) {
        addPassengerBtn.addEventListener('click', function () {
            const rows = passengersContainer.querySelectorAll('.passenger-row');
            if (rows.length >= MAX_PASSENGERS) {
                alert('Maximum 6 passengers allowed per booking.');
                return;
            }

            const newIndex = rows.length + 1;
            const newRow = document.createElement('div');
            newRow.className = 'passenger-row p-4 bg-slate-50 border border-slate-200 rounded-lg space-y-3 transition-all';
            newRow.innerHTML = `
                <div class="flex items-center justify-between border-b border-slate-200 pb-2">
                    <span class="passenger-num font-semibold text-slate-700">Passenger ${newIndex}</span>
                    <button type="button" class="remove-passenger-btn text-rose-600 hover:text-rose-800 text-sm font-medium flex items-center gap-1">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                        Remove
                    </button>
                </div>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Full Name</label>
                        <input type="text" name="passenger_name[]" required placeholder="e.g. Rahul Sharma"
                               class="w-full px-3 py-2 text-sm border border-slate-300 rounded focus:ring-2 focus:ring-sky-500 focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Age</label>
                        <input type="number" name="passenger_age[]" min="1" max="120" required placeholder="Age (1-120)"
                               class="w-full px-3 py-2 text-sm border border-slate-300 rounded focus:ring-2 focus:ring-sky-500 focus:outline-none">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-600 mb-1">Gender</label>
                        <select name="passenger_gender[]" required
                                class="w-full px-3 py-2 text-sm border border-slate-300 rounded focus:ring-2 focus:ring-sky-500 focus:outline-none bg-white">
                            <option value="MALE">Male</option>
                            <option value="FEMALE">Female</option>
                            <option value="OTHER">Other</option>
                        </select>
                    </div>
                </div>
            `;

            passengersContainer.appendChild(newRow);
            updateCalculations();
        });
    }

    // Event delegation for removing passenger rows
    passengersContainer.addEventListener('click', function (e) {
        const removeBtn = e.target.closest('.remove-passenger-btn');
        if (removeBtn) {
            const row = removeBtn.closest('.passenger-row');
            if (row) {
                row.remove();
                updateCalculations();
            }
        }
    });

    // Initial calculation on load
    updateCalculations();
});
