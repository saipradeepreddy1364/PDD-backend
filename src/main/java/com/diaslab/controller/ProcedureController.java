package com.diaslab.controller;

import com.diaslab.model.StepRequest;
import com.diaslab.model.StepResponse;
import com.diaslab.service.ProcedureService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.Map;

@RestController
@RequestMapping("/api")
public class ProcedureController {

    private final ProcedureService procedureService;

    public ProcedureController(ProcedureService procedureService) {
        this.procedureService = procedureService;
    }

    // ── Health check ──────────────────────────────────────────────────────────
    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        return ResponseEntity.ok(Map.of(
                "status", "UP",
                "service", "PDD Pradeep Backend",
                "port", "8080"));
    }

    // ── Predict next step (main endpoint) ─────────────────────────────────────
    @PostMapping("/next-step")
    public ResponseEntity<StepResponse> getNextStep(
            @Valid @RequestBody StepRequest request) {
        StepResponse response = procedureService.getNextStep(request);
        return ResponseEntity.ok(response);
    }

    // ── Get full workflow ──────────────────────────────────────────────────────
    @GetMapping("/workflow")
    public ResponseEntity<Map<String, Object>> getWorkflow(
            @RequestParam String procedure,
            @RequestParam String subtype) {
        Map<String, Object> workflow = procedureService.getFullWorkflow(procedure, subtype);
        return ResponseEntity.ok(workflow);
    }

    // ── ML model info ──────────────────────────────────────────────────────────
    @GetMapping("/model-info")
    public ResponseEntity<Map<String, Object>> getModelInfo() {
        Map<String, Object> info = procedureService.getModelInfo();
        return ResponseEntity.ok(info);
    }

    // ── Get procedures list ───────────────────────────────────────────────────
    @GetMapping("/procedures")
    public ResponseEntity<Map<String, Object>> getProcedures() {
        Map<String, Object> procedures = procedureService.getProcedures();
        return ResponseEntity.ok(procedures);
    }
}