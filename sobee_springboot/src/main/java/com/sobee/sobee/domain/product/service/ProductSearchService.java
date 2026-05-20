package com.sobee.sobee.domain.product.service;

import com.sobee.sobee.domain.product.dto.SearchResultDto;
import com.sobee.sobee.domain.product.entity.CardInfo;
import com.sobee.sobee.domain.product.entity.CardTopBenefit;
import com.sobee.sobee.domain.product.entity.InsuranceProduct;
import com.sobee.sobee.domain.product.entity.SavingsProduct;
import com.sobee.sobee.domain.product.repository.CardInfoRepository;
import com.sobee.sobee.domain.product.repository.InsuranceProductRepository;
import com.sobee.sobee.domain.product.repository.SavingsProductRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.*;
import java.util.stream.Collectors;

@Slf4j
@Service
@RequiredArgsConstructor
public class ProductSearchService {

    private final CardInfoRepository cardInfoRepository;
    private final SavingsProductRepository savingsProductRepository;
    private final InsuranceProductRepository insuranceProductRepository;

    public SearchResultDto search(String query) {
        if (query == null || query.isBlank()) {
            return SearchResultDto.builder()
                    .keyword(query)
                    .totalCount(0)
                    .cards(List.of())
                    .savings(List.of())
                    .insurance(List.of())
                    .build();
        }

        List<String> tokens = Arrays.stream(query.trim().split("[\\s,]+"))
                .filter(t -> t.length() >= 1)
                .distinct()
                .collect(Collectors.toList());

        log.info("🔍 검색 쿼리: '{}' → 토큰: {}", query, tokens);

        List<CardInfo> cards = searchCards(tokens);
        List<SavingsProduct> savings = searchSavings(tokens);
        List<InsuranceProduct> insurance = searchInsurance(tokens);

        List<SearchResultDto.CardResult> cardResults = cards.stream()
                .map(c -> SearchResultDto.CardResult.builder()
                        .cardInfoId(c.getCardInfoId())
                        .gorillaId(c.getGorillaId())
                        .cardName(c.getCardName())
                        .corpName(c.getCorpName())
                        .cardType(c.getCardType())
                        .annualFeeBasic(c.getAnnualFeeBasic())
                        .minPerformance(c.getMinPerformance())
                        .cardImgUrl(c.getCardImgUrl())
                        .isDiscontinued(c.getIsDiscontinued())
                        .topBenefitTitles(c.getTopBenefits().stream()
                                .map(CardTopBenefit::getTitle)
                                .collect(Collectors.toList()))
                        .build())
                .collect(Collectors.toList());

        List<SearchResultDto.SavingsResult> savingsResults = savings.stream()
                .map(s -> SearchResultDto.SavingsResult.builder()
                        .savingsId(s.getSavingsId())
                        .korCoNm(s.getKorCoNm())
                        .finPrdtNm(s.getFinPrdtNm())
                        .saveTrm(s.getSaveTrm())
                        .intrRate(s.getIntrRate())
                        .intrMaxRate(s.getIntrMaxRate())
                        .spclCnd(s.getSpclCnd())
                        .build())
                .collect(Collectors.toList());

        List<SearchResultDto.InsuranceResult> insuranceResults = insurance.stream()
                .map(i -> SearchResultDto.InsuranceResult.builder()
                        .productId(i.getProductId())
                        .productName(i.getProductName())
                        .insurer(i.getInsurer())
                        .category(i.getCategory())
                        .situationTags(i.getSituationTags())
                        .coveragePeriodDays(i.getCoveragePeriodDays())
                        .productUrl(i.getProductUrl())
                        .build())
                .collect(Collectors.toList());

        int total = cardResults.size() + savingsResults.size() + insuranceResults.size();
        log.info("✅ 검색 결과 — 카드: {}건, 예적금: {}건, 보험: {}건", cardResults.size(), savingsResults.size(), insuranceResults.size());

        return SearchResultDto.builder()
                .keyword(query)
                .totalCount(total)
                .cards(cardResults)
                .savings(savingsResults)
                .insurance(insuranceResults)
                .build();
    }

    private List<CardInfo> searchCards(List<String> tokens) {
        Map<Long, CardInfo> resultMap = new LinkedHashMap<>();
        for (String token : tokens) {
            cardInfoRepository.searchByKeyword(token)
                    .forEach(c -> resultMap.put(c.getCardInfoId(), c));
        }
        return new ArrayList<>(resultMap.values());
    }

    private List<SavingsProduct> searchSavings(List<String> tokens) {
        Map<Long, SavingsProduct> resultMap = new LinkedHashMap<>();
        for (String token : tokens) {
            savingsProductRepository.searchByKeyword(token)
                    .forEach(s -> resultMap.put(s.getSavingsId(), s));
        }
        return new ArrayList<>(resultMap.values());
    }

    private List<InsuranceProduct> searchInsurance(List<String> tokens) {
        Map<String, InsuranceProduct> resultMap = new LinkedHashMap<>();
        for (String token : tokens) {
            insuranceProductRepository.searchByKeyword(token)
                    .forEach(i -> resultMap.put(i.getProductId(), i));
        }
        return new ArrayList<>(resultMap.values());
    }
}