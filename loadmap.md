# [개발 지침] 경로 탐색 서비스 MVP 개발 상세 로드맵

---

### **프로젝트 현황 (2025년 7월 21일 월요일 기준)**

#### **완료된 작업 (Completed Tasks)**

*   **백엔드 (Backend)**
    *   FastAPI 기반 프로젝트 구조 및 핵심 로직(DB, 스키마, 경로탐색, API 라우터) 골격 구현 완료.
    *   PostgreSQL + PostGIS 환경 설정 및 `osm2pgsql`, `scripts/import_data.py`를 통한 데이터 임포트 완료.
    *   주요 백엔드 오류(SRID 불일치, `psycopg2`, `pydantic` 관련) 해결.
    *   `pathfinder.py`의 SQL 쿼리에서 `F_NODE`, `T_NODE` 컬럼 참조 오류 수정 완료.
    *   핵심 기능 API 구현 완료:
        *   `POST /route`: 도로 스냅핑(snapping)을 포함한 최단 경로 탐색.
        *   `GET /search`: Trigram을 활용한 장소(POI) 검색. 검색 결과에 주소 정보 포함하도록 개선 완료.

*   **프론트엔드 (Frontend) - React 마이그레이션**
    *   기존 정적 HTML/CSS/JS 코드를 **React + TypeScript** 기반의 모던 웹 애플리케이션으로 마이그레이션 결정.
    *   `Vite`를 사용하여 새로운 React 프로젝트(`frontend`) 생성 완료.
    *   `axios`, `leaflet`, `react-leaflet` 등 필수 라이브러리 설치 완료.
    *   `App.tsx`, `index.css` 등 기본 컴포넌트 및 스타일 구조 설정 완료.
    *   Leaflet CSS를 `index.html`에 추가하여 지도 스타일링 준비 완료.
    *   백엔드 CORS 설정(`backend/main.py`) 업데이트 완료 (프론트엔드 개발 서버 포트 허용).
    *   `MapComponent` 생성 및 지도 렌더링, 클릭 이벤트 처리 구현 완료.
    *   `SearchComponent` 생성 및 장소 검색 UI 구현 완료.
    *   검색 결과 선택 시 지도 해당 위치로 자동 줌인 및 이동 기능 구현 완료.
    *   검색 결과 목록에 장소 주소 표시 기능 구현 완료.

#### **알려진 문제 및 개선 사항 (Known Issues & Future Improvements)**

*   **총 거리 0.00km 표시 문제:** (해결된 것으로 보이나, React 마이그레이션 후 재검증 필요) 경로가 정상적으로 그려지지만, `total_distance_meters`가 0으로 표시되는 문제.
*   **부분 경로 시각화 미흡:** 현재 경로 계산 시 거리는 정확하지만, 지도에 표시되는 경로는 출발/도착 지점의 부분 경로(snapped point -> node)가 제외된 채 그려짐. `ST_LineSubstring` 등을 사용하여 세 조각의 경로를 모두 연결하여 보여주는 시각적 개선이 필요함.
*   **알고리즘 고도화:** 현재는 최단 거리만 계산. 향후 교통량, 도로 종류(고속도로 등)를 고려한 가중치 부여 및 '최소 시간' 경로 탐색 기능 추가 필요.
*   **위치 기반 검색:** 현재 지도 뷰의 중심 좌표를 기준으로 가까운 장소가 검색 결과 상위에 노출되도록 `GET /search` API를 고도화.
*   **후보 경로 표시:** 최단 경로 외에 여러 경로 옵션(예: 최소 시간 경로, 추천 경로)을 제공하고 사용자가 선택할 수 있도록 기능 확장.

---

### **다음 단계 (To-Do List) - React 프론트엔드 구현**

1.  **API 연동 및 상태 관리 로직 구체화:**
    *   **목표:** `App.tsx`에서 백엔드 API 연동 및 전체 애플리케이션 상태 관리 로직 완성.
    *   **세부 계획:**
        *   `handleRouteSearch` 함수 내에서 `axios`를 사용하여 `POST /route` API 호출.
        *   API 호출 시 `loading` 상태를 true로 설정하여 사용자에게 피드백 제공.
        *   API 응답 성공 시 `route` 상태 업데이트, 실패 시 오류 메시지 표시.
        *   `handleMapClick`, `handleSearchSelect` 함수에서 출발/도착지(`startPoint`, `endPoint`) 상태 업데이트 로직 구체화.

2.  **UI/UX 개선:**
    *   **목표:** 사용자 편의성을 높이고 서비스의 완성도를 향상.
    *   **세부 계획:**
        *   경로 탐색 및 검색 시 로딩 인디케이터(스피너 등) 표시.
        *   출발지/도착지 마커 및 정보 초기화 버튼 추가.
        *   검색 결과 목록 디자인 개선 및 스크롤 기능 추가.
        *   오류 메시지를 사용자 친화적으로 프론트엔드에 표시.

---

**프로젝트 개요:**

**목표:** '국가표준 노드/링크' 데이터와 오픈소스 데이터를 활용하여, 사용자가 지도 위에서 경로를 탐색하고 장소를 검색할 수 있는 웹 기반 MVP(Minimum Viable Product)를 개발한다.

**핵심 기술 스택:**
*   **데이터베이스:** PostgreSQL + PostGIS
*   **백엔드:** Python, FastAPI, NetworkX, GeoAlchemy2
*   **프론트엔드 (신규):** **React, TypeScript, Vite, Leaflet, React-Leaflet, Axios**
*   **좌표계:**
    *   **백엔드/DB:** EPSG:5186 (ITRF2000 / Central Belt) - 데이터 처리 및 계산용
    *   **프론트엔드/API:** EPSG:4326 (WGS84) - 위도/경도 표준

---

### **OpenStreetMap 소스 코드 기반 개선 계획 (OpenStreetMap Source Code Based Improvement Plan)**

**목표:** OpenStreetMap 웹사이트의 실제 소스 코드를 분석하여, 검증된 검색 및 경로 탐색 로직을 우리 프로젝트에 맞게 도입하고 기능을 고도화한다.

**참고 소스 코드:** `./openstreetmap/openstreetmap-website/`

**1차 개선 대상:**
*   **장소 검색 (Search):** `planet_osm_point` 테이블을 넘어, OpenStreetMap에서 사용하는 Geocoding/Search 서비스(예: Nominatim)의 원리를 파악하고, 관련성 높은 검색 결과를 제공하도록 백엔드 API를 개선한다.