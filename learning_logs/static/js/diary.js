document.addEventListener('DOMContentLoaded', function() {
    initCalendar();
    initAutosave();
    initModal();
    initDragAndDrop();
    initTheme();
    initNav();
    initCropper();
});

// --- X-Calendar AJAX Navigation ---
function initCalendar() {
    const calendarContainer = document.querySelector('.calendar-container');
    if (!calendarContainer) return;

    calendarContainer.addEventListener('click', function(e) {
        const btn = e.target.closest('.js-calendar-nav');
        if (!btn) return;

        e.preventDefault();
        const year = btn.dataset.year;
        const month = btn.dataset.month;

        fetchCalendar(year, month);
    });
}

function fetchCalendar(year, month) {
    const wrapper = document.querySelector('.calendar-wrapper');
    wrapper.style.opacity = '0.5';

    fetch(`/api/calendar/?year=${year}&month=${month}`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.text();
        })
        .then(html => {
            wrapper.innerHTML = html;
            wrapper.style.opacity = '1';
            
            // Update navigation buttons
            updateNavButtons(year, month);
            
            // Re-attach modal listeners to new calendar cells
            initModal();
            initDragAndDrop();
        })
        .catch(error => {
            console.error('Error fetching calendar:', error);
            wrapper.style.opacity = '1';
        });
}

function updateNavButtons(currentYear, currentMonth) {
    // Simple logic to calculate next/prev month for button updates
    // In a real app, you might return this metadata from the API
    let year = parseInt(currentYear);
    let month = parseInt(currentMonth);
    
    const prevDate = new Date(year, month - 2, 1); // JS months are 0-indexed
    const nextDate = new Date(year, month, 1);

    const prevBtn = document.querySelector('.js-nav-prev');
    const nextBtn = document.querySelector('.js-nav-next');

    if (prevBtn) {
        prevBtn.dataset.year = prevDate.getFullYear();
        prevBtn.dataset.month = prevDate.getMonth() + 1;
    }
    if (nextBtn) {
        nextBtn.dataset.year = nextDate.getFullYear();
        nextBtn.dataset.month = nextDate.getMonth() + 1;
    }
}

// --- Autosave Feature ---
function initAutosave() {
    const form = document.querySelector('.js-autosave-form');
    if (!form) return;

    let timeout = null;
    const statusIndicator = document.getElementById('autosave-status');

    form.addEventListener('input', function() {
        if (statusIndicator) statusIndicator.textContent = 'Typing...';
        
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            saveDraft(new FormData(form));
        }, 2000); // Autosave after 2 seconds of inactivity
    });

    function saveDraft(formData) {
        if (statusIndicator) statusIndicator.textContent = 'Saving draft...';

        fetch('/api/autosave/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        })
        .then(res => res.json())
        .then(data => {
            if (statusIndicator) {
                statusIndicator.textContent = 'Draft saved';
                setTimeout(() => statusIndicator.textContent = '', 3000);
            }
        })
        .catch(err => {
            console.error('Autosave failed', err);
            if (statusIndicator) statusIndicator.textContent = 'Save failed';
        });
    }
}

// --- Image Cropper ---
function initCropper() {
    const imageInput = document.querySelector('input[name="image"]');
    const modal = document.getElementById('cropperModal');
    const image = document.getElementById('imageToCrop');
    const cropBtn = document.getElementById('cropAndSave');
    let cropper;

    if (!imageInput || !modal || !image) return;

    imageInput.addEventListener('change', function(e) {
        const files = e.target.files;
        if (files && files.length > 0) {
            const file = files[0];
            const reader = new FileReader();
            
            reader.onload = function(event) {
                image.src = event.target.result;
                modal.classList.add('active');
                
                if (cropper) {
                    cropper.destroy();
                }
                cropper = new Cropper(image, {
                    aspectRatio: 1,
                    viewMode: 1,
                    minContainerWidth: 300,
                    minContainerHeight: 300,
                });
            };
            reader.readAsDataURL(file);
        }
    });

    cropBtn.addEventListener('click', function() {
        if (!cropper) return;

        cropper.getCroppedCanvas({
            width: 300,
            height: 300,
        }).toBlob(function(blob) {
            // Create a new file from the blob
            const file = new File([blob], "profile_cropped.jpg", { type: "image/jpeg" });
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            imageInput.files = dataTransfer.files;
            modal.classList.remove('active');
        }, 'image/jpeg');
    });
}

// --- Modal Logic ---
function initModal() {
    const modal = document.getElementById('eventModal');
    const closeBtns = document.querySelectorAll('.close-modal');
    const newEventBtn = document.getElementById('btn-new-event');
    const calendarDays = document.querySelectorAll('.calendar__day:not(.calendar__day--empty)');
    const dateInput = document.querySelector('input[name="event_date"]');

    if (!modal) return;

    // Open modal on "New Event" button
    if (newEventBtn) {
        newEventBtn.addEventListener('click', () => {
            modal.classList.add('active');
        });
    }

    // Open modal on Calendar Day click
    calendarDays.forEach(day => {
        day.addEventListener('click', (e) => {
            // Don't trigger if clicking an existing event pill (optional, maybe open edit view)
            if (e.target.classList.contains('event-pill')) return;

            const dateStr = day.dataset.date; // YYYY-MM-DD
            if (dateStr && dateInput) {
                // Set the date input value (requires format YYYY-MM-DDTHH:MM)
                const now = new Date();
                const timeStr = now.toTimeString().slice(0,5); // HH:MM
                dateInput.value = `${dateStr}T${timeStr}`;
            }
            modal.classList.add('active');
        });
    });

    // Close modal
    closeBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            modal.classList.remove('active');
        });
    });

    // Close on outside click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });
}

// --- Theme Toggle ---
function initTheme() {
    const toggleBtn = document.getElementById('theme-toggle');
    const html = document.documentElement;
    const icon = toggleBtn ? toggleBtn.querySelector('i') : null;

    // Check local storage
    const currentTheme = localStorage.getItem('theme');
    if (currentTheme) {
        html.setAttribute('data-theme', currentTheme);
        if (icon) icon.className = currentTheme === 'light' ? 'fas fa-sun' : 'fas fa-moon';
    }

    if (toggleBtn) {
        toggleBtn.addEventListener('click', () => {
            const theme = html.getAttribute('data-theme') === 'light' ? 'dark' : 'light';
            html.setAttribute('data-theme', theme);
            localStorage.setItem('theme', theme);
            if (icon) icon.className = theme === 'light' ? 'fas fa-sun' : 'fas fa-moon';
        });
    }
}

// --- Navbar Toggler ---
function initNav() {
    const toggler = document.querySelector('.navbar__toggler');
    const collapse = document.querySelector('.navbar__collapse');

    if (toggler && collapse) {
        toggler.addEventListener('click', () => {
            toggler.classList.toggle('active');
            collapse.classList.toggle('active');
        });
    }
}

// --- Drag and Drop Logic ---
function initDragAndDrop() {
    const events = document.querySelectorAll('.event-pill');
    const days = document.querySelectorAll('.calendar__day:not(.calendar__day--empty)');

    events.forEach(event => {
        event.addEventListener('dragstart', dragStart);
        event.addEventListener('dragend', dragEnd);
    });

    days.forEach(day => {
        day.addEventListener('dragover', dragOver);
        day.addEventListener('dragenter', dragEnter);
        day.addEventListener('dragleave', dragLeave);
        day.addEventListener('drop', dragDrop);
    });
}

function dragStart(e) {
    e.dataTransfer.setData('text/plain', e.target.dataset.entryId);
    setTimeout(() => {
        e.target.classList.add('dragging');
    }, 0);
}

function dragEnd(e) {
    e.target.classList.remove('dragging');
}

function dragOver(e) {
    e.preventDefault(); // Necessary to allow dropping
}

function dragEnter(e) {
    e.preventDefault();
    this.classList.add('calendar__day--drag-over');
}

function dragLeave(e) {
    this.classList.remove('calendar__day--drag-over');
}

function dragDrop(e) {
    e.preventDefault();
    this.classList.remove('calendar__day--drag-over');
    
    const entryId = e.dataTransfer.getData('text/plain');
    const newDate = this.dataset.date;
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;

    fetch('/api/update_entry_date/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({ entry_id: entryId, date: newDate })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // Refresh calendar to show moved event
            const currentBtn = document.querySelector('.js-nav-next');
            // We use the "next" button's data to figure out current view, 
            // or simply reload the current month logic.
            // A simpler way is to trigger a click on a hidden refresh button or re-fetch.
            // For now, let's just re-fetch the current view based on the header buttons.
            const prevBtn = document.querySelector('.js-nav-prev');
            // If prev is showing month X, then current is month X+1
            let year = parseInt(prevBtn.dataset.year);
            let month = parseInt(prevBtn.dataset.month) + 1;
            if (month > 12) { month = 1; year++; }
            
            fetchCalendar(year, month);
        } else {
            alert('Failed to move event: ' + data.message);
        }
    });
}