document.addEventListener('DOMContentLoaded', function () {
    function getFieldRow(inputElement, fieldClass) {
        if (!inputElement) return null;
        let row = inputElement.closest(`.form-row, .${fieldClass}`) || inputElement.parentElement;
        while (row && row.parentElement && !row.classList.contains('form-row') && !row.classList.contains(fieldClass) && row.parentElement.tagName !== 'FIELDSET' && row.parentElement.tagName !== 'FORM') {
            if (row.parentElement.classList.contains('form-row') || row.parentElement.classList.contains(fieldClass) || row.parentElement.querySelector(`label[for="${inputElement.id}"]`)) {
                row = row.parentElement;
                break;
            }
            row = row.parentElement;
        }
        return row;
    }

    function initCustomPromptToggle() {
        const checkbox = document.querySelector('input[name="custom_prompt"]');
        const textarea = document.querySelector('textarea[name="custom_prompt_text"]');
        if (!checkbox || !textarea) return;

        const row = getFieldRow(textarea, 'field-custom_prompt_text');
        if (!row) return;

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

    function initDisableThinkingToggle() {
        const select = document.querySelector('select[name="llm_model"]');
        const disableThinkingInput = document.querySelector('input[name="disable_thinking"]');
        if (!select || !disableThinkingInput) return;

        const row = getFieldRow(disableThinkingInput, 'field-disable_thinking');
        if (!row) return;

        function updateThinkingVisibility() {
            const val = (select.value || '').toLowerCase();
            if (val.includes('gemma')) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        }

        select.removeEventListener('change', updateThinkingVisibility);
        select.addEventListener('change', updateThinkingVisibility);
        updateThinkingVisibility();
    }

    function initGFSStorageTypeToggle() {
        const storageSelect = document.querySelector('select[name="storage_type"]');
        if (!storageSelect) return;

        const responseModeSelect = document.querySelector('select[name="response_mode"]');
        const useHydeCheckbox = document.querySelector('input[name="use_hyde"]');
        const synthesizerCheckbox = document.querySelector('input[name="synthesizer"]');
        const embeddingSelect = document.querySelector('select[name="embedding_model"]');
        const llmSelect = document.querySelector('select[name="llm_model"]');

        function updateGFSParameters() {
            const isGoogle = (storageSelect.value === 'google');

            // 1. Response Mode
            if (responseModeSelect) {
                const row = getFieldRow(responseModeSelect, 'field-response_mode');
                if (isGoogle) {
                    responseModeSelect.value = 'compact';
                    responseModeSelect.disabled = true;
                    if (row) row.style.opacity = '0.5';
                } else {
                    responseModeSelect.disabled = false;
                    if (row) row.style.opacity = '1.0';
                }
            }

            // 2. Use HyDE
            if (useHydeCheckbox) {
                const row = getFieldRow(useHydeCheckbox, 'field-use_hyde');
                if (isGoogle) {
                    useHydeCheckbox.checked = false;
                    useHydeCheckbox.disabled = true;
                    if (row) row.style.opacity = '0.5';
                } else {
                    useHydeCheckbox.disabled = false;
                    if (row) row.style.opacity = '1.0';
                }
            }

            // 3. Synthesizer
            if (synthesizerCheckbox) {
                const row = getFieldRow(synthesizerCheckbox, 'field-synthesizer');
                if (isGoogle) {
                    synthesizerCheckbox.checked = false;
                    synthesizerCheckbox.disabled = true;
                    if (row) row.style.opacity = '0.5';
                } else {
                    synthesizerCheckbox.disabled = false;
                    if (row) row.style.opacity = '1.0';
                }
            }


            // 5. Embedding Model
            if (embeddingSelect) {
                const row = getFieldRow(embeddingSelect, 'field-embedding_model');
                if (isGoogle) {
                    embeddingSelect.disabled = true;
                    if (row) row.style.opacity = '0.5';
                } else {
                    embeddingSelect.disabled = false;
                    if (row) row.style.opacity = '1.0';
                }
            }

            // 6. LLM Model
            if (llmSelect) {
                const allowedGFSModels = ['gemini-2.5-flash-lite', 'gemini-3.5-flash-lite', 'gemini-3.7-flash'];
                const options = Array.from(llmSelect.options);
                options.forEach(opt => {
                    if (isGoogle) {
                        if (!allowedGFSModels.includes(opt.value)) {
                            opt.disabled = true;
                            opt.hidden = true;
                        } else {
                            opt.disabled = false;
                            opt.hidden = false;
                        }
                    } else {
                        opt.disabled = false;
                        opt.hidden = false;
                    }
                });

                if (isGoogle && !allowedGFSModels.includes(llmSelect.value)) {
                    llmSelect.value = 'gemini-2.5-flash-lite';
                }

                // Trigger change event to update disable_thinking visibility
                llmSelect.dispatchEvent(new Event('change'));
            }
        }

        // Before submit, re-enable fields so their values are sent to Django
        const form = storageSelect.closest('form');
        if (form) {
            form.addEventListener('submit', function() {
                if (responseModeSelect) responseModeSelect.disabled = false;
                if (useHydeCheckbox) useHydeCheckbox.disabled = false;
                if (synthesizerCheckbox) synthesizerCheckbox.disabled = false;
                if (embeddingSelect) embeddingSelect.disabled = false;
                if (llmSelect) {
                    Array.from(llmSelect.options).forEach(opt => { opt.disabled = false; });
                }
            });
        }

        storageSelect.removeEventListener('change', updateGFSParameters);
        storageSelect.addEventListener('change', updateGFSParameters);
        updateGFSParameters();
    }

    initCustomPromptToggle();
    initDisableThinkingToggle();
    initGFSStorageTypeToggle();
    setTimeout(function() {
        initCustomPromptToggle();
        initDisableThinkingToggle();
        initGFSStorageTypeToggle();
    }, 300);
    setTimeout(function() {
        initCustomPromptToggle();
        initDisableThinkingToggle();
        initGFSStorageTypeToggle();
    }, 1000);
});
