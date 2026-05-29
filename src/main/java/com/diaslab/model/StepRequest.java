package com.diaslab.model;

import jakarta.validation.constraints.NotBlank;

public class StepRequest {

    @NotBlank(message = "Procedure is required")
    private String procedure;

    @NotBlank(message = "Subtype is required")
    private String subtype;

    @NotBlank(message = "Current step is required")
    private String currentStep;

    // Getters and Setters
    public String getProcedure() {
        return procedure;
    }

    public void setProcedure(String procedure) {
        this.procedure = procedure;
    }

    public String getSubtype() {
        return subtype;
    }

    public void setSubtype(String subtype) {
        this.subtype = subtype;
    }

    public String getCurrentStep() {
        return currentStep;
    }

    public void setCurrentStep(String currentStep) {
        this.currentStep = currentStep;
    }
}