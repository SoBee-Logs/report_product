package com.sobee.sobee.domain.product.controller;

import com.sobee.sobee.domain.product.entity.InsuranceProduct;
import com.sobee.sobee.domain.product.entity.SavingsProduct;
import com.sobee.sobee.domain.product.repository.SavingsProductRepository;
import com.sobee.sobee.domain.product.service.InsuranceProductService;
import com.sobee.sobee.domain.product.service.SavingsProductSyncService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api/financial-products")
@RequiredArgsConstructor
public class FinancialProductController {

    private final SavingsProductSyncService savingsSyncService;
    private final SavingsProductRepository savingsRepo;
    private final InsuranceProductService insuranceService;

    // ===== 예적금 =====

    @PostMapping("/savings/sync")
    public ResponseEntity<Map<String, Object>> syncSavings() {
        int count = savingsSyncService.syncAll();
        return ResponseEntity.ok(Map.of("status", "success", "synced", count));
    }

    @GetMapping("/savings")
    public ResponseEntity<List<SavingsProduct>> getSavings() {
        return ResponseEntity.ok(savingsRepo.findAll());
    }

    @GetMapping("/savings/top")
    public ResponseEntity<List<SavingsProduct>> getTopSavings() {
        return ResponseEntity.ok(savingsRepo.findTop10ByOrderByIntrMaxRateDesc());
    }

    @GetMapping("/savings/search")
    public ResponseEntity<List<SavingsProduct>> searchSavings(@RequestParam String keyword) {
        return ResponseEntity.ok(savingsRepo.searchByKeyword(keyword));
    }

    // ===== 미니보험 =====

    @GetMapping("/insurance")
    public ResponseEntity<List<InsuranceProduct>> getInsurance() {
        return ResponseEntity.ok(insuranceService.findAll());
    }

    @GetMapping("/insurance/category/{category}")
    public ResponseEntity<List<InsuranceProduct>> getInsuranceByCategory(@PathVariable String category) {
        return ResponseEntity.ok(insuranceService.findByCategory(category));
    }

    @GetMapping("/insurance/age/{age}")
    public ResponseEntity<List<InsuranceProduct>> getInsuranceByAge(@PathVariable int age) {
        return ResponseEntity.ok(insuranceService.findByAge(age));
    }

    @GetMapping("/insurance/search")
    public ResponseEntity<List<InsuranceProduct>> searchInsurance(@RequestParam String keyword) {
        return ResponseEntity.ok(insuranceService.search(keyword));
    }
}