package com.diaslab.model;

public class StepResponse {
    private String procedure;
    private String subtype;
    private String currentStep;
    private String nextStep;
    private double confidence;
    private String message;
    private boolean success;

    // Constructors
    public StepResponse() {}

    public StepResponse(String procedure, String subtype, String currentStep, String nextStep, double confidence, String message, boolean success) {
        this.procedure = procedure;
        this.subtype = subtype;
        this.currentStep = currentStep;
        this.nextStep = nextStep;
        this.confidence = confidence;
        this.message = message;
        this.success = success;
    }

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

    public String getNextStep() {
        return nextStep;
    }

    public void setNextStep(String nextStep) {
        this.nextStep = nextStep;
    }

    public double getConfidence() {
        return confidence;
    }

    public void setConfidence(double confidence) {
        this.confidence = confidence;
    }

    public String getMessage() {
        return message;
    }

    public void setMessage(String message) {
        this.message = message;
    }

    public boolean isSuccess() {
        return success;
    }

    public void setSuccess(boolean success) {
        this.success = success;
    }
}