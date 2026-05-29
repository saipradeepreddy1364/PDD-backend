package com.diaslab.service;

import com.diaslab.model.StepRequest;
import com.diaslab.model.StepResponse;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.ParameterizedTypeReference;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;

@Service
public class ProcedureService {

    private static final Logger log = LoggerFactory.getLogger(ProcedureService.class);

    private final RestTemplate restTemplate;

    @Value("${flask.api.url}")
    private String flaskApiUrl;

    public ProcedureService(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    // ── Predict next single step ──────────────────────────────────────────────
    public StepResponse getNextStep(StepRequest request) {
        String url = flaskApiUrl + "/api/next-step";
        log.debug("Calling Flask → {} with procedure={}, subtype={}, currentStep={}",
                url, request.getProcedure(), request.getSubtype(), request.getCurrentStep());

        Map<String, String> body = new HashMap<>();
        body.put("procedure", request.getProcedure());
        body.put("subtype", request.getSubtype());
        body.put("current_step", request.getCurrentStep());

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, String>> entity = new HttpEntity<>(body, headers);

        try {
            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url, HttpMethod.POST, entity,
                    new ParameterizedTypeReference<Map<String, Object>>() {
                    });

            Map<String, Object> responseBody = response.getBody();
            if (responseBody == null)
                throw new RuntimeException("Empty response from Flask");

            StepResponse stepResponse = new StepResponse();
            stepResponse.setProcedure(request.getProcedure());
            stepResponse.setSubtype(request.getSubtype());
            stepResponse.setCurrentStep(request.getCurrentStep());
            stepResponse.setNextStep((String) responseBody.get("next_step"));
            stepResponse.setConfidence(
                    ((Number) responseBody.get("confidence")).doubleValue());
            stepResponse.setMessage("Next step predicted successfully");
            stepResponse.setSuccess(true);
            return stepResponse;

        } catch (Exception e) {
            log.error("Flask API call failed: {}", e.getMessage());
            StepResponse error = new StepResponse();
            error.setProcedure(request.getProcedure());
            error.setSubtype(request.getSubtype());
            error.setCurrentStep(request.getCurrentStep());
            error.setNextStep("Could not predict next step");
            error.setMessage("ML API error: " + e.getMessage());
            error.setSuccess(false);
            return error;
        }
    }

    // ── Predict full workflow from start ──────────────────────────────────────
    public Map<String, Object> getFullWorkflow(String procedure, String subtype) {
        String url = flaskApiUrl + "/api/predict-full";
        log.debug("Calling Flask full workflow → procedure={}, subtype={}", procedure, subtype);

        Map<String, String> body = new HashMap<>();
        body.put("procedure", procedure);
        body.put("subtype", subtype);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, String>> entity = new HttpEntity<>(body, headers);

        try {
            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url, HttpMethod.POST, entity,
                    new ParameterizedTypeReference<Map<String, Object>>() {
                    });
            return response.getBody();
        } catch (Exception e) {
            log.error("Flask full workflow call failed: {}", e.getMessage());
            Map<String, Object> error = new HashMap<>();
            error.put("error", e.getMessage());
            error.put("success", false);
            return error;
        }
    }

    // ── Get ML model metadata ─────────────────────────────────────────────────
    public Map<String, Object> getModelInfo() {
        String url = flaskApiUrl + "/api/model-info";
        try {
            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url, HttpMethod.GET,
                    null,
                    new ParameterizedTypeReference<Map<String, Object>>() {
                    });
            return response.getBody();
        } catch (Exception e) {
            log.error("Flask model-info call failed: {}", e.getMessage());
            Map<String, Object> error = new HashMap<>();
            error.put("error", "ML API not reachable: " + e.getMessage());
            error.put("success", false);
            return error;
        }
    }

    // ── Get procedures list ───────────────────────────────────────────────────
    public Map<String, Object> getProcedures() {
        String url = flaskApiUrl + "/api/procedures";
        try {
            ResponseEntity<Map<String, Object>> response = restTemplate.exchange(
                    url, HttpMethod.GET,
                    null,
                    new ParameterizedTypeReference<Map<String, Object>>() {
                    });
            return response.getBody();
        } catch (Exception e) {
            log.error("Flask procedures call failed: {}", e.getMessage());
            Map<String, Object> error = new HashMap<>();
            error.put("error", "ML API not reachable: " + e.getMessage());
            error.put("success", false);
            return error;
        }
    }
}