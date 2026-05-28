package com.diaslab.model;

import lombok.Data;
import jakarta.validation.constraints.NotBlank;

@Data
public class StepRequest {

    @NotBlank(message = "Procedure is required")
    private String procedure;

    @NotBlank(message = "Subtype is required")
    private String subtype;

    @NotBlank(message = "Current step is required")
    private String currentStep;
}