package com.diaslab.model;

import lombok.Data;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;

@Data
@AllArgsConstructor
@NoArgsConstructor
public class StepResponse {
    private String procedure;
    private String subtype;
    private String currentStep;
    private String nextStep;
    private double confidence;
    private String message;
    private boolean success;
}