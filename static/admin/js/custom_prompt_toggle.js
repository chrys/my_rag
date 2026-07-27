document.addEventListener('DOMContentLoaded', function () {
    function initCustomPromptToggle() {
        const checkbox = document.querySelector('input[name="custom_prompt"]');
        const textarea = document.querySelector('textarea[name="custom_prompt_text"]');
        if (!checkbox || !textarea) return;

        // Locate the form field container row for custom_prompt_text
        let row = textarea.closest('.form-row, .field-custom_prompt_text') || textarea.parentElement;
        
        // Find outer wrapper in case of custom admin themes (like Unfold)
        while (row && row.parentElement && !row.classList.contains('form-row') && !row.classList.contains('field-custom_prompt_text') && row.parentElement.tagName !== 'FIELDSET' && row.parentElement.tagName !== 'FORM') {
            if (row.parentElement.classList.contains('form-row') || row.parentElement.classList.contains('field-custom_prompt_text') || row.parentElement.querySelector('label[for="id_custom_prompt_text"]')) {
                row = row.parentElement;
                break;
            }
            row = row.parentElement;
        }

        function updateVisibility() {
            if (checkbox.checked) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }

        checkbox.removeEventListener('change', updateVisibility);
        checkbox.addEventListener('change', updateVisibility);
        updateVisibility();
    }

    initCustomPromptToggle();
    setTimeout(initCustomPromptToggle, 300);
    setTimeout(initCustomPromptToggle, 1000);
});
