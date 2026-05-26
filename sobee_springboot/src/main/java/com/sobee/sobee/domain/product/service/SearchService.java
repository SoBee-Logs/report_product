package com.sobee.sobee.domain.product.service;

import com.sobee.sobee.domain.product.dto.ParsedSearchDto;
import com.sobee.sobee.domain.product.dto.SearchRequestDto;
import com.sobee.sobee.domain.product.dto.SearchResponseDto;
import com.sobee.sobee.domain.product.dto.SearchResultDto;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;

@Slf4j
@Service
@RequiredArgsConstructor
public class SearchService {

    private final ProductSearchService productSearchService;
    private final RestTemplate restTemplate;

    @Value("${fastapi.base-url:http://localhost:8000}")
    private String fastapiBaseUrl;

    public SearchResponseDto search(SearchRequestDto request) {
        String keyword = request.getSearch_input();

        ParsedSearchDto parsed = callParseSearch(keyword);

        SearchResultDto result = (parsed != null)
                ? productSearchService.searchStructured(parsed, keyword)
                : productSearchService.search(keyword);

        String aiText = (parsed != null && parsed.getAi_text() != null && !parsed.getAi_text().isBlank())
                ? parsed.getAi_text()
                : "'" + keyword + "' 관련 상품을 찾았어요. 총 " + result.getTotalCount() + "개의 상품이 있어요.";

        List<SearchResponseDto.ProductDto> products = new ArrayList<>();

        for (SearchResultDto.CardResult c : result.getCards()) {
            String cardUrl = c.getGorillaId() != null
                    ? "https://www.card-gorilla.com/card/detail/" + c.getGorillaId()
                    : "";

            String header = (c.getTopBenefitTitles() != null && !c.getTopBenefitTitles().isEmpty())
                    ? c.getTopBenefitTitles().get(0)
                    : "";

            String middle = "";
            if (c.getMinPerformance() != null && c.getMinPerformance() > 0) {
                middle += "전월 실적 " + String.format("%,d", c.getMinPerformance()) + "원 이상";
            }
            if (c.getAnnualFeeBasic() != null && !c.getAnnualFeeBasic().isBlank()) {
                middle += (middle.isEmpty() ? "" : " / ") + "연회비 " + c.getAnnualFeeBasic();
            }

            String small = (c.getTopBenefitTitles() != null && c.getTopBenefitTitles().size() > 1)
                    ? String.join(", ", c.getTopBenefitTitles().subList(1, c.getTopBenefitTitles().size()))
                    : "";

            products.add(SearchResponseDto.ProductDto.builder()
                    .product_name(c.getCardName())
                    .product_company(c.getCorpName())
                    .product_img_url(c.getCardImgUrl())
                    .product_type("card")
                    .is_discontinued(Boolean.TRUE.equals(c.getIsDiscontinued()))
                    .content(SearchResponseDto.ContentDto.builder()
                            .header(header)
                            .middle(middle)
                            .small(small)
                            .url(cardUrl)
                            .build())
                    .build());
        }

        for (SearchResultDto.SavingsResult s : result.getSavings()) {
            products.add(SearchResponseDto.ProductDto.builder()
                    .product_name(s.getFinPrdtNm())
                    .product_company(s.getKorCoNm())
                    .product_img_url(null)
                    .product_type("savings")
                    .content(SearchResponseDto.ContentDto.builder()
                            .header(s.getIntrMaxRate() != null ? "우대금리 최대 " + s.getIntrMaxRate() + "%" : "")
                            .middle(s.getSaveTrm() != null ? s.getSaveTrm() + "개월" : "")
                            .small(s.getSpclCnd() != null ? s.getSpclCnd() : "")
                            .url("")
                            .build())
                    .build());
        }

        for (SearchResultDto.InsuranceResult i : result.getInsurance()) {
            products.add(SearchResponseDto.ProductDto.builder()
                    .product_name(i.getProductName())
                    .product_company(i.getInsurer())
                    .product_img_url(null)
                    .product_type("insurance")
                    .content(SearchResponseDto.ContentDto.builder()
                            .header(i.getCategory() != null ? i.getCategory() : "")
                            .middle(i.getSituationTags() != null ? i.getSituationTags() : "")
                            .small(i.getCoveragePeriodDays() != null ? "보장기간 " + i.getCoveragePeriodDays() + "일" : "")
                            .url(i.getProductUrl() != null ? i.getProductUrl() : "")
                            .build())
                    .build());
        }

        return SearchResponseDto.builder()
                .AI_text(aiText)
                .products(products)
                .build();
    }

    private ParsedSearchDto callParseSearch(String query) {
        try {
            ResponseEntity<ParsedSearchDto> response = restTemplate.postForEntity(
                    fastapiBaseUrl + "/internal/parse-search",
                    Map.of("query", query),
                    ParsedSearchDto.class);
            return response.getBody();
        } catch (Exception e) {
            log.warn("GPT 파싱 실패, 키워드 검색으로 폴백: {}", e.getMessage());
            return null;
        }
    }
}
