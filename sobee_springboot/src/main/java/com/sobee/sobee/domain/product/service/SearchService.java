package com.sobee.sobee.domain.product.service;

import com.sobee.sobee.domain.product.dto.SearchRequestDto;
import com.sobee.sobee.domain.product.dto.SearchResponseDto;
import com.sobee.sobee.domain.product.dto.SearchResultDto;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.ArrayList;
import java.util.List;

@Service
@RequiredArgsConstructor
public class SearchService {

    private final ProductSearchService productSearchService;

    public SearchResponseDto search(SearchRequestDto request) {
        String keyword = request.getSearch_input();

        SearchResultDto result = productSearchService.search(keyword);

        List<SearchResponseDto.ProductDto> products = new ArrayList<>();

        // 카드
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

        // 예적금
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

        // 미니보험
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
                .AI_text("'" + keyword + "' 관련 상품을 찾았어요. 총 " + result.getTotalCount() + "개의 상품이 있어요.")
                .products(products)
                .build();
    }
}